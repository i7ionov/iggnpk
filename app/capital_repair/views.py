import os
from datetime import date
from rest_framework.response import Response
from rest_framework import permissions
from capital_repair.tasks import send_acts, generate_excel
from dictionaries.serializers import UserSerializer
from iggnpk import settings
from tools.history_serializer import HistorySerializer
from tools.viewsets import DevExtremeViewSet
from . import services
from .acts import Act
from .analytic import CrReport
from .analytic_serializers import CrReportSerializer
from .models import CreditOrganization, Notify, ContributionsInformation, ContributionsInformationMistake
from .serializers import NotifySerializer, \
    ContributionsInformationSerializer, ContributionsInformationMistakeSerializer, CreditOrganizationSerializer
from rest_framework.decorators import action
from rest_framework import viewsets


class CreditOrganizationsViewSet(DevExtremeViewSet):
    lookup_fields = ['inn', 'name']
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = CreditOrganization.objects.all()
    serializer_class = CreditOrganizationSerializer

    def search_filter(self, queryset):
        return queryset.filter(allow_to_select=True)


class NotifiesViewSet(DevExtremeViewSet):
    service = services.NotifyService()
    queryset = Notify.objects.all()
    additional_fields = service.private_fields
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
        generate_excel.delay(os.path.join(settings.MEDIA_ROOT, 'templates', 'notifies.xlsx'), list(ids), 'capital_repair.notify', user.data['email'])
        return Response({},
                        status=200)

    @action(detail=True)
    def get_history(self, request, pk=None):
        if request.user.is_staff is False:
            return Response('У вас нет соответствующих прав', status=400)
        serializer = HistorySerializer(instance=self.get_object().history.all(), many=True)
        return Response(serializer.data)


class ContributionsInformationViewSet(DevExtremeViewSet):
    service = services.ContributionsInformationService()
    queryset = ContributionsInformation.objects.all()
    serializer_class = ContributionsInformationSerializer
    lookup_fields = ['id', 'notify__account_number', 'notify__house__address__area','notify__house__address__city', 'notify__house__address__street', 'notify__house__number']
    additional_fields = service.private_fields

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
        generate_excel.delay(os.path.join(settings.MEDIA_ROOT, 'templates', 'contributions.xlsx'), list(ids),
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
