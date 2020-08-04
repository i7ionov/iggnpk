from datetime import datetime

from django.db.models import Q
from rest_framework.parsers import FileUploadParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from tools.serializer_tools import upd_foreign_key
from .models import CreditOrganization, Branch, Notify, NotifyStatus
from dictionaries.models import Organization, House, File
from .serializers import CreditOrganisationSerializer, BranchSerializer, NotifySerializer
from rest_framework.decorators import api_view
from rest_framework import viewsets
from tools import dev_extreme
from django.shortcuts import get_object_or_404


class CreditOrganisationsViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = CreditOrganization.objects.all()
    serializer_class = CreditOrganisationSerializer

    def list(self, request):
        if 'group' in request.GET:
            d, total_count = dev_extreme.populate_group_category(request, CreditOrganization)
            data = {"totalCount": total_count, "items": d}
        else:
            queryset, total_count = dev_extreme.filtered_query(request, CreditOrganization)
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
        else: return Response()


class BranchViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

    def list(self, request):
        if 'group' in request.GET:
            d, total_count = dev_extreme.populate_group_category(request, Branch)
            data = {"totalCount": total_count, "items": d}
        else:
            queryset, total_count = dev_extreme.filtered_query(request, Branch)
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
        else: return Response()


class NotifiesViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = Notify.objects.all()
    serializer_class = NotifySerializer

    def list(self, request):
        exclude_fields = []
        if not request.user.is_staff:
            exclude_fields.append('comment2')

        if 'group' in request.GET:
            d, total_count = dev_extreme.populate_group_category(request, Notify)
            data = {"totalCount": total_count, "items": d}
        else:
            queryset, total_count = dev_extreme.filtered_query(request, Notify)
            serializer = NotifySerializer(queryset, many=True, exclude=exclude_fields)
            data = {'items': serializer.data, 'totalCount': total_count}
        return Response(data)

    def retrieve(self, request, pk=None):
        exclude_fields = []
        if not request.user.is_staff:
            exclude_fields.append('comment2')

        queryset = Notify.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = NotifySerializer(item, exclude=exclude_fields)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        exclude_fields = []
        if not request.user.is_staff:
            exclude_fields.append('comment2')
        item = NotifySerializer(data=request.data, exclude=exclude_fields)
        item.is_valid()
        if item.is_valid():
            status = NotifyStatus.objects.get(id=1)
            branch = Branch.objects.get(id=request.data['credit_organization_branch']['id'])
            house, created = House.objects.get_or_create(address_id=request.data['house']['address']['id'], number=request.data['house']['number'])

            if request.user.is_staff:
                org = Organization.objects.get(id=request.data['organization']['id'])
            else:
                org = request.user.organization
            item.save(organization=org, date=datetime.today().date(), status=status,
                      credit_organization_branch=branch, house=house)
            return Response(item.data)
        else:
            return Response(status=400)

    def update(self, request, *args, **kwargs):
        exclude_fields = []
        if not request.user.is_staff:
            exclude_fields.append('comment2')
        data = request.data
        instance = self.get_object()
        serializer = self.serializer_class(instance=instance, data=data, partial=True, exclude=exclude_fields)
        serializer.is_valid(raise_exception=True)
        if request.user.is_staff:
            org = upd_foreign_key('organization', data, instance, Organization)
        else:
            org = instance.organization
        branch = upd_foreign_key('credit_organization_branch', data, instance, Branch)
        house = House.objects.get_or_create_new('house', data, instance)
        status = upd_foreign_key('status', data, instance, NotifyStatus)
        if 'files' in data:
            files = []
            if data['files'] != 'empty':
                for file in data['files']:
                    files.append(File.objects.get(id=file['id']))
        else:
            files = instance.files.all()

        serializer.save(organization=org, credit_organization_branch=branch, house=house, files=files, status=status)
        return Response(serializer.data)
