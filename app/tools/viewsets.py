from django.db.models import Q
from loguru import logger
from rest_framework import viewsets, mixins, permissions
from rest_framework.response import Response
from tools import dev_extreme
from tools.ip_addr import get_client_ip
from tools.permissions import ModelPermissions
from tools.service import ServiceException


class DevExtremeViewSet(viewsets.ModelViewSet, mixins.ListModelMixin):
    permission_classes = [permissions.IsAuthenticated, ModelPermissions]
    service = None
    queryset = None
    search_queryset_for_all = None
    search_queryset_for_uk = None
    additional_fields = None
    lookup_fields = None
    totalCount = None
    serializer_class = None

    def get_exclude_fields(self):
        if not self.request.user.is_staff:
            return self.additional_fields

    def get_serializer_class(self):
        return self.serializer_class

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        if self.get_exclude_fields():
            kwargs['exclude'] = self.get_exclude_fields()
        return serializer_class(*args, **kwargs)

    def get_serializer_context(self):
        context = super(DevExtremeViewSet, self).get_serializer_context()
        return context

    def search_filter(self, queryset):
        return queryset

    def list_filter(self, queryset):
        return queryset

    def filter_queryset(self, queryset):
        if 'group' in self.request.GET:
            queryset = self.list_filter(queryset)
            queryset, self.totalCount = dev_extreme.populate_group_category(self.request.GET, queryset)
        else:
            if 'searchValue' in self.request.GET:
                queryset = self.search_filter(queryset)
                searchValue = self.request.GET['searchValue'].strip('"').replace(',', ' ').split(' ')
                keywords = [x for x in searchValue if x]
                for keyword in keywords:
                    q = Q()
                    for field in self.lookup_fields:
                        q = q | Q(**{field + '__icontains': keyword})
                    queryset = queryset.filter(q)
            else:
                queryset = self.list_filter(queryset)
            queryset, total_queryset, self.totalCount = dev_extreme.filtered_query(self.request.GET, queryset)
        return queryset

    def list(self, request, *args, **kwargs):
        if 'group' in request.GET:
            d, total_count = dev_extreme.populate_group_category(request.GET, self.queryset)
            data = {"totalCount": total_count, "items": d}
        else:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            data = {'items': serializer.data,
                    'totalCount': self.totalCount,
                    'summary': [self.totalCount]}
        return Response(data)

    def create(self, request, *args, **kwargs):
        logger.info(
            f"{request.user.username} ip:{get_client_ip(request)} " +
            f"trying to create {self.queryset.model._meta.verbose_name} " +
            f"with data {request.data}")
        try:
            data = self.service.create(request.data, request.user)
            logger.info(
                f"{request.user.username} ip:{get_client_ip(request)} " +
                f"succesfully created {self.queryset.model._meta.verbose_name} with " +
                f"object id: {data['id']}")
            return Response(data)
        except ServiceException as e:
            logger.info(
                f"{request.user.username} ip:{get_client_ip(request)} " +
                f"failed to create {self.queryset.model._meta.verbose_name} " +
                f"with data {request.data}. Error: {e.errors}")

            return Response(e.errors, status=400)

    def update(self, request, *args, **kwargs):
        logger.info(
            f"{request.user.username} ip:{get_client_ip(request)} " +
            f"trying to update {self.queryset.model._meta.verbose_name} with id: {kwargs['pk']} " +
            f"with data {request.data}")

        try:
            data = self.service.update(self.get_object(), request.data, request.user)
            logger.info(
                f"{request.user.username} ip:{get_client_ip(request)} " +
                f"succesfully updated {self.queryset.model._meta.verbose_name} " +
                f"object id: {data['id']}")

            return Response(data)
        except ServiceException as e:
            logger.info(
                f"{request.user.username} ip:{get_client_ip(request)} " +
                f"failed to update {self.queryset.model._meta.verbose_name} with id: {kwargs['pk']}" +
                f"with data {request.data}. Error: {e.errors}")
            return Response(e.errors, status=400)

    def destroy(self, request, *args, **kwargs):
        logger.info(
            f"{request.user.username} ip:{get_client_ip(request)} " +
            f"trying to delete {self.queryset.model._meta.verbose_name} with id: {kwargs['pk']} " +
            f"with data {request.data}")

        try:
            self.service.delete(self.get_object(), request.user)
            logger.info(
                f"{request.user.username} ip:{get_client_ip(request)} " +
                f"succesfully delete {self.queryset.model._meta.verbose_name} " +
                f"object id: {kwargs['pk']}")

            return Response(status=204)
        except ServiceException as e:
            logger.info(
                f"{request.user.username} ip:{get_client_ip(request)} " +
                f"failed to delete {self.queryset.model._meta.verbose_name} with id: {kwargs['pk']}" +
                f"with data {request.data}. Error: {e.errors}")
            return Response(e.errors, status=400)
