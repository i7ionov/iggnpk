import io
import os
from datetime import datetime
from django.db.models import Avg, Sum
from django.db.models import Q
from rest_framework.parsers import FileUploadParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.http import HttpResponse
from iggnpk import settings
from tools.docx_response import docx_response
from tools import date
from tools.serializer_tools import upd_foreign_key, upd_many_to_many
from .models import CreditOrganization, Branch, Notify, Status, ContributionsInformation, ContributionsInformationMistake
from dictionaries.models import Organization, House, File
from .serializers import CreditOrganisationSerializer, BranchSerializer, NotifySerializer, \
    ContributionsInformationSerializer, ContributionsInformationMistakeSerializer
from rest_framework.decorators import api_view
from rest_framework import viewsets
from tools import dev_extreme
from django.shortcuts import get_object_or_404
from docxtpl import DocxTemplate


class CreditOrganisationsViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = CreditOrganization.objects.all()
    serializer_class = CreditOrganisationSerializer

    def list(self, request):
        if 'group' in request.GET:
            d, total_count = dev_extreme.populate_group_category(request, CreditOrganization)
            data = {"totalCount": total_count, "items": d}
        else:
            queryset, total_queryset, total_count = dev_extreme.filtered_query(request, CreditOrganization)
            serializer = self.serializer_class(queryset, many=True)
            data = {'items': serializer.data, 'totalCount': total_count}
        return Response(data)

    def retrieve(self, request, pk=None):
        item = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(item)
        return Response(serializer.data)

    def search(self, request):
        if 'searchValue' in request.GET:
            searchValue = request.GET['searchValue'].strip('"').replace(',', ' ').split(' ')
            keywords = [x for x in searchValue if x]
            queryset = self.queryset
            for keyword in keywords:
                queryset = queryset.filter(Q(inn__icontains=keyword) | Q(name__icontains=keyword))
            serializer = self.serializer_class(queryset, many=True)
            data = {'items': serializer.data}
            return Response(data)
        else:
            return Response()


class BranchViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

    def list(self, request):
        if 'group' in request.GET:
            d, total_count = dev_extreme.populate_group_category(request, Branch)
            data = {"totalCount": total_count, "items": d}
        else:
            queryset, total_queryset, total_count = dev_extreme.filtered_query(request, Branch)
            serializer = BranchSerializer(queryset, many=True)
            data = {'items': serializer.data, 'totalCount': total_count}
        return Response(data)

    def retrieve(self, request, pk=None):
        queryset = Branch.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = BranchSerializer(item)
        return Response(serializer.data)

    def search(self, request):
        if 'searchValue' in request.GET:
            searchValue = request.GET['searchValue'].strip('"').replace(',', ' ').split(' ')
            keywords = [x for x in searchValue if x]
            queryset = self.queryset
            for keyword in keywords:
                queryset = queryset.filter(Q(address__icontains=keyword) | Q(kpp__icontains=keyword))
            serializer = self.serializer_class(queryset, many=True)
            data = {'items': serializer.data}
            return Response(data)
        else:
            return Response()


class NotifiesViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = Notify.objects.all()
    serializer_class = NotifySerializer

    def list(self, request):
        exclude_fields = []
        if not request.user.is_staff:
            exclude_fields.append('comment2')
            exclude_fields.append('date_of_exclusion')
            exclude_fields.append('account_closing_date')
            exclude_fields.append('ground_for_exclusion')
            exclude_fields.append('source_of_information')
        # пользователь видит уведомления только своей организации
        if not request.user.is_staff:
            queryset = self.queryset.filter(organization_id=request.user.organization.id)
        else:
            queryset = self.queryset
        if 'group' in request.GET:
            d, total_count = dev_extreme.populate_group_category(request, queryset)
            data = {"totalCount": total_count, "items": d}
        else:
            queryset, total_queryset, total_count = dev_extreme.filtered_query(request, queryset)
            serializer = NotifySerializer(queryset, many=True, exclude=exclude_fields)
            data = {'items': serializer.data,
                    'totalCount': total_count,
                    'summary': [total_count]}
        return Response(data)

    def retrieve(self, request, pk=None):
        exclude_fields = []
        if not request.user.is_staff:
            exclude_fields.append('comment2')
            exclude_fields.append('date_of_exclusion')
            exclude_fields.append('account_closing_date')
            exclude_fields.append('ground_for_exclusion')
            exclude_fields.append('source_of_information')
        # пользователь видит уведомления только своей организации
        if not request.user.is_staff:
            queryset = self.queryset.filter(organization_id=request.user.organization.id)
        else:
            queryset = self.queryset
        item = get_object_or_404(queryset, pk=pk)
        serializer = NotifySerializer(item, exclude=exclude_fields)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        exclude_fields = []
        if not request.user.is_staff:
            exclude_fields.append('comment2')
            exclude_fields.append('date_of_exclusion')
            exclude_fields.append('account_closing_date')
            exclude_fields.append('ground_for_exclusion')
            exclude_fields.append('source_of_information')
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
            exclude_fields.append('comment2')
            exclude_fields.append('date_of_exclusion')
            exclude_fields.append('account_closing_date')
            exclude_fields.append('ground_for_exclusion')
            exclude_fields.append('source_of_information')

        serializer = self.serializer_class(instance=instance, data=data, partial=True, exclude=exclude_fields)
        serializer.is_valid(raise_exception=True)
        if request.user.is_staff:
            org = upd_foreign_key('organization', data, instance, Organization)
        else:
            org = instance.organization
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
        else:
            status = instance.status

        if 'files' in data:
            files = []
            if data['files'] != 'empty':
                for file in data['files']:
                    files.append(File.objects.get(id=file['id']))
        else:
            files = instance.files.all()

        serializer.save(organization=org, bank=bank, house=house, files=files, status=status)
        return Response(serializer.data)

    def search(self, request):
        queryset = self.queryset
        if request.user.is_staff == False:
            queryset = queryset.filter(status_id=3)  # поиск только по активным уведомлениям
            queryset = queryset.filter(organization_id=request.user.organization.id)  # и только по своим
        if 'searchValue' in request.GET:
            searchValue = request.GET['searchValue'].strip('"').replace(',', ' ').split(' ')
            keywords = [x for x in searchValue if x]
            for keyword in keywords:
                queryset = queryset.filter(
                    Q(id__icontains=keyword) |
                    Q(account_number__contains=keyword) |
                    Q(house__address__area__icontains=keyword) |
                    Q(house__address__city__icontains=keyword) |
                    Q(house__address__street__icontains=keyword) |
                    Q(house__number__icontains=keyword))
            queryset = queryset[:10]
            serializer = self.serializer_class(queryset, many=True)
            data = {'items': serializer.data}
            return Response(data)
        else:
            queryset = queryset[:10]
            serializer = self.serializer_class(queryset, many=True)
            data = {'items': serializer.data}
            return Response(data)


class ContributionsInformationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = ContributionsInformation.objects.all()
    serializer_class = ContributionsInformationSerializer

    def list(self, request):
        exclude_fields = []
        if not request.user.is_staff:
            exclude_fields.append('comment2')
        # пользователь видит уведомления только своей организации
        if not request.user.is_staff:
            queryset = self.queryset.filter(notify__organization_id=request.user.organization.id)
        else:
            queryset = self.queryset
        if 'group' in request.GET:
            d, total_count = dev_extreme.populate_group_category(request, queryset)
            data = {"totalCount": total_count, "items": d}
        else:
            queryset, total_queryset, total_count = dev_extreme.filtered_query(request, queryset)
            serializer = self.serializer_class(queryset, many=True, exclude=exclude_fields)
            data = {'items': serializer.data,
                    'totalCount': total_count,
                    'summary': [total_count]}

        return Response(data)

    def retrieve(self, request, pk=None):
        exclude_fields = []
        if not request.user.is_staff:
            exclude_fields.append('comment2')
        # пользователь видит уведомления только своей организации
        if not request.user.is_staff:
            queryset = self.queryset.filter(notify__organization_id=request.user.organization.id)
        else:
            queryset = self.queryset
        item = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(item, exclude=exclude_fields)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        exclude_fields = []
        if not request.user.is_staff:
            exclude_fields.append('comment2')
        item = self.serializer_class(data=request.data, exclude=exclude_fields)
        item.is_valid()
        if item.is_valid():
            if request.data['status']['id'] > 2:
                return Response('Неправильный статус', status=400)
            status = Status.objects.get(id=request.data['status']['id'])
            notify = Notify.objects.get(id=request.data['notify']['id'])
            if notify.organization.id != request.user.organization.id and not request.user.is_staff:
                return Response({'Организация, указанная в уведомлениии, не соответствует организации пользователя'},
                                status=400)
            files = upd_many_to_many('files',request, None, File)
            mistakes = upd_many_to_many('mistakes', request, None, ContributionsInformationMistake)
            item.save(date=datetime.today().date(), status=status, files=files, notify=notify, mistakes=mistakes)
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

        notify = upd_foreign_key('notify', data, instance, Notify)
        if notify.organization.id != request.user.organization.id and not request.user.is_staff:
            return Response({'Организация, указанная в уведомлениии, не соответствует организации пользователя'},
                            status=400)

        files = upd_many_to_many('files', request, instance, File)
        mistakes = upd_many_to_many('mistakes', request, instance, ContributionsInformationMistake)

        if status.id == 3:
            notify.latest_contrib_date = datetime.now().date()
            notify.save()
        serializer.save(files=files, status=status, notify=notify, mistakes=mistakes)
        return Response(serializer.data)


class ContributionsInformationMistakeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = ContributionsInformationMistake.objects.all()
    serializer_class = ContributionsInformationMistakeSerializer

    def list(self, request):
        if 'group' in request.GET:
            d, total_count = dev_extreme.populate_group_category(request, self.queryset)
            data = {"totalCount": total_count, "items": d}
        else:
            queryset, total_queryset, total_count = dev_extreme.filtered_query(request, self.queryset)
            serializer = self.serializer_class(queryset, many=True)
            data = {'items': serializer.data, 'totalCount': total_count}
        return Response(data)

    def retrieve(self, request, pk=None):
        item = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(item)
        return Response(serializer.data)

    def search(self, request):
        queryset = self.queryset
        if 'searchValue' in request.GET:
            searchValue = request.GET['searchValue'].strip('"').replace(',', ' ').split(' ')
            keywords = [x for x in searchValue if x]
            for keyword in keywords:
                queryset = queryset.filter(
                    Q(text__icontains=keyword))

            queryset = queryset[:10]
            serializer = self.serializer_class(queryset, many=True)
            data = {'items': serializer.data}
            return Response(data)
        else:
            queryset = queryset[:10]
            serializer = self.serializer_class(queryset, many=True)
            data = {'items': serializer.data}
            return Response(data)


def generate_act(self, pk=None):
    if pk:
        doc = DocxTemplate(os.path.join(settings.MEDIA_ROOT, 'templates', 'act.docx'))
        contrib_info = ContributionsInformation.objects.get(pk=pk)
        if datetime.now() < datetime(datetime.now().year,3,20):
            month = date.MONTH_NAMES[11]
        elif datetime.now() < datetime(datetime.now().year,6,20):
            month = date.MONTH_NAMES[2]
        elif datetime.now() < datetime(datetime.now().year,9,20):
            month = date.MONTH_NAMES[5]
        else:
            month = date.MONTH_NAMES[8]
        context = {'date': date.russian_date(datetime.now()),
                   'org': contrib_info.notify.organization,
                   'house': contrib_info.notify.house,
                   'month': month,
                   'year': datetime.now().year}
        doc.render(context)
        return docx_response(doc, 'act')
    else:
        return Response({'error': 'Не указан id сведений'}, status=400)