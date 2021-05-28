import io
import os
from datetime import datetime, date
from io import BytesIO
from django.contrib.auth.decorators import permission_required
from django.db.models import Avg, Sum
from django.db.models import Q
from rest_framework.parsers import FileUploadParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, mixins
from django.http import HttpResponse

from capital_repair.tasks import send_acts, generate_excel
from dictionaries.serializers import UserSerializer
from iggnpk import settings
from tools import date_tools
from tools.export_to_excel import export_to_excel
from tools.history_serializer import HistorySerializer
from tools.permissions import ModelPermissions
from tools.serializer_tools import upd_foreign_key, upd_many_to_many
from tools.viewsets import DevExtremeViewSet
from .acts import Act
from .analytic import CrReport
from .analytic_serializers import CrReportSerializer
from .models import CreditOrganization, Branch, Notify, Status, ContributionsInformation, ContributionsInformationMistake
from dictionaries.models import Organization, House, File
from .serializers import NotifySerializer, \
    ContributionsInformationSerializer, ContributionsInformationMistakeSerializer, CreditOrganizationSerializer
from rest_framework.decorators import api_view, action
from rest_framework import viewsets
from tools import dev_extreme
from django.shortcuts import get_object_or_404
from docxtpl import DocxTemplate
import zipfile
from django.db.models import Sum


class CreditOrganizationsViewSet(DevExtremeViewSet):
    lookup_fields = ['inn', 'name']
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = CreditOrganization.objects.all()
    serializer_class = CreditOrganizationSerializer

    def search_filter(self, queryset):
        return queryset.filter(allow_to_select=True)


class NotifiesViewSet(DevExtremeViewSet):
    queryset = Notify.objects.all()
    additional_fields = ['comment2','date_of_exclusion','account_closing_date', 'ground_for_exclusion', 'source_of_information']
    lookup_fields = ['id', 'account_number', 'house__address__area','house__address__city', 'house__address__street', 'house__number']
    serializer_class = NotifySerializer

    def search_filter(self, queryset):
        if not self.request.user.is_staff:
            return queryset.filter(organization_id=self.request.user.organization.id)
        else:
            return queryset

    def list_filter(self, queryset):
        if not self.request.user.is_staff:
            return queryset.filter(organization_id=self.request.user.organization.id)
        else:
            return queryset

    def create(self, request, *args, **kwargs):
        exclude_fields = []
        if not request.user.is_staff:
            exclude_fields.extend(self.additional_fields)
        item = NotifySerializer(data=request.data, exclude=exclude_fields)
        item.is_valid()
        if item.is_valid():
            if request.data['status']['id'] > 2:
                return Response('Неправильный статус', status=400)
            status = Status.objects.get(id=request.data['status']['id'])
            bank = CreditOrganization.objects.get(id=request.data['bank']['id'])
            house, created = House.objects.get_or_create(address_id=request.data['house']['address']['id'],
                                                         number=str(request.data['house']['number']).strip().lower())

            if request.user.is_staff:
                org = Organization.objects.get(id=request.data['organization']['id'])
            else:
                org = request.user.organization
            files = []
            if 'files' in request.data:
                if request.data['files'] != 'empty':
                    for file in request.data['files']:
                        files.append(File.objects.get(id=file['id']))

            item.save(organization=org, date=datetime.today().date(), status=status,
                      bank=bank, files=files, house=house)
            return Response(item.data)
        else:
            return Response(item.errors, status=400)

    def update(self, request, *args, **kwargs):
        exclude_fields = []
        data = request.data
        instance = self.get_object()

        if not request.user.is_staff:
            if instance.status.id > 2:
                return Response('Вы не можете редактировать эту запись', status=400)
            if data['status']['id'] > 2:
                return Response('Неправильный статус', status=400)
            exclude_fields.extend(self.additional_fields)

        serializer = self.get_serializer_class()(instance=instance, data=data, partial=True, exclude=exclude_fields)
        serializer.is_valid(raise_exception=True)
        if request.user.is_staff:
            org = upd_foreign_key('organization', data, instance, Organization)
        else:
            org = instance.organization
        if request.user.is_staff and 'date' in data:
            date = data['date']
        else:
            date = instance.date
        bank = upd_foreign_key('bank', data, instance, CreditOrganization)
        house = House.objects.get_or_create_new('house', data, instance)
        if 'status' in data and 'id' in data['status']:
            if instance.status is not None and data['status']['id'] == instance.status.id:
                status = instance.status
            else:
                status = Status.objects.get(id=data['status']['id'])
                # присваиваем всем другим записям с этим домом статус Исключено
                if status.text == 'Согласовано':
                    Notify.objects.filter(house_id=house.id, status_id=3).update(status_id=4,
                                                                                 date_of_exclusion=datetime.now())
                    house.organization = org
                    house.save()
        else:
            status = instance.status

        if 'files' in data:
            files = []
            if data['files'] != 'empty':
                for file in data['files']:
                    files.append(File.objects.get(id=file['id']))
        else:
            files = instance.files.all()

        serializer.save(organization=org, bank=bank, house=house, files=files, status=status, date=date)
        return Response(serializer.data)

    @action(detail=False)
    def generate_acts(self, request):
        if request.user.is_staff is False:
            return Response('У вас нет соответствующих прав', status=400)
        user = UserSerializer(request.user)
        send_acts.delay(request.GET, user.data['email'])
        return Response({},
                        status=200)

    @action(detail=False)
    def export_to_excel(self, request):
        if request.user.is_staff is False:
            return Response('У вас нет соответствующих прав', status=400)
        user = UserSerializer(request.user)
        ids = self.filter_queryset(self.queryset).values_list('id', flat=True)
        generate_excel.delay(request.GET, os.path.join(settings.MEDIA_ROOT, 'templates', 'notifies.xlsx'), list(ids), 'capital_repair.notify', user.data['email'])
        return Response({},
                        status=200)

    @action(detail=True)
    def get_history(self, request, pk=None):
        if request.user.is_staff is False:
            return Response('У вас нет соответствующих прав', status=400)
        serializer = HistorySerializer(instance=self.get_object().history.all(), many=True)
        return Response(serializer.data)


class ContributionsInformationViewSet(DevExtremeViewSet):
    queryset = ContributionsInformation.objects.all()
    serializer_class = ContributionsInformationSerializer
    lookup_fields = ['id', 'notify__account_number', 'notify__house__address__area','notify__house__address__city', 'notify__house__address__street', 'notify__house__number']
    additional_fields = ['comment2']

    def search_filter(self, queryset):
        if not self.request.user.is_staff:
            return self.queryset.filter(notify__organization_id=self.request.user.organization.id)
        else:
            return queryset

    def list_filter(self, queryset):
        if not self.request.user.is_staff:
            return self.queryset.filter(notify__organization_id=self.request.user.organization.id)
        else:
            return queryset

    def create(self, request, *args, **kwargs):
        item = self.get_serializer(data=request.data)
        item.is_valid()
        if item.is_valid():
            if request.data['status']['id'] > 2:
                return Response('Неправильный статус', status=400)
            status = Status.objects.get(id=request.data['status']['id'])
            notify = Notify.objects.get(id=request.data['notify']['id'])
            try:
                last_contrib = notify.last_contrib
                last_contrib.last_notify = None
                last_contrib.save()
            except ContributionsInformation.DoesNotExist:
                pass
            if notify.organization.id != request.user.organization.id and not request.user.is_staff:
                return Response({'Организация, указанная в уведомлениии, не соответствует организации пользователя'},
                                status=400)
            files = upd_many_to_many('files',request, None, File)
            if request.user.is_staff:
                mistakes = upd_many_to_many('mistakes', request, None, ContributionsInformationMistake)
            else:
                mistakes = []
            item.save(date=datetime.today().date(), status=status, files=files, notify=notify, last_notify=notify, mistakes=mistakes)
            return Response(item.data)
        else:
            return Response(item.errors, status=400)

    def update(self, request, *args, **kwargs):
        exclude_fields = []
        data = request.data
        instance = self.get_object()

        if not request.user.is_staff:
            if request.data['status']['id'] > 2:
                return Response('Неправильный статус', status=400)
            if instance.status.id > 2:
                return Response('Вы не можете редактировать эту запись', status=400)
            exclude_fields.append('comment2')

        serializer = self.serializer_class(instance=instance, data=data, partial=True, exclude=exclude_fields)
        serializer.is_valid(raise_exception=True)
        if 'status' in data and 'id' in data['status']:
            if instance.status is not None and data['status']['id'] == instance.status.id:
                status = instance.status
            else:
                status = Status.objects.get(id=data['status']['id'])
        else:
            status = instance.status

        if request.user.is_staff and 'date' in request.data:
            date = request.data['date']
        else:
            date = instance.date

        notify = upd_foreign_key('notify', data, instance, Notify)
        try:
            last_contrib = notify.last_contrib
            last_contrib.last_notify = None
            last_contrib.save()
        except ContributionsInformation.DoesNotExist:
            pass


        if notify.organization.id != request.user.organization.id and not request.user.is_staff:
            return Response({'Организация, указанная в уведомлениии, не соответствует организации пользователя'},
                            status=400)

        files = upd_many_to_many('files', request, instance, File)
        if request.user.is_staff:
            mistakes = upd_many_to_many('mistakes', request, instance, ContributionsInformationMistake)
        else:
            mistakes = instance.mistakes.all()
        serializer.save(files=files, status=status, notify=notify, last_notify=notify, mistakes=mistakes, date=date)
        return Response(serializer.data)

    @action(detail=True)
    def get_history(self, request, pk=None):
        if request.user.is_staff is False:
            return Response('У вас нет соответствующих прав', status=400)
        serializer = HistorySerializer(instance=self.get_object().history.all(), many=True)
        return Response(serializer.data)

    @action(detail=False)
    def export_to_excel(self, request):
        if request.user.is_staff is False:
            return Response('У вас нет соответствующих прав', status=400)
        user = UserSerializer(request.user)
        ids = self.filter_queryset(self.queryset).values_list('id', flat=True)
        generate_excel.delay(request.GET, os.path.join(settings.MEDIA_ROOT, 'templates', 'contributions.xlsx'), list(ids),
                             'capital_repair.contributionsinformation', user.data['email'])
        return Response({},
                        status=200)


class ContributionsInformationMistakeViewSet(DevExtremeViewSet):
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = ContributionsInformationMistake.objects.all()
    serializer_class = ContributionsInformationMistakeSerializer
    lookup_fields = ['text']


class DashboardViewSet(viewsets.ViewSet):
    @action(detail=False)
    def cr_report(self, request):
        date_start = date(date.today().year, Act.report_month(), 1)
        date_end = date.today()
        if 'date_start' in request.GET and 'date_end' in request.GET:
            date_start = request.GET['date_start']
            date_end = request.GET['date_end']
        print(date_start, date_end)
        report = CrReport(date_start, date_end)
        serializer = CrReportSerializer(report)
        return Response(serializer.data)
