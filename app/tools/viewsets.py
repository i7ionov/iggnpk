from django.db.models import Q
from rest_framework import viewsets, mixins, permissions
from rest_framework.response import Response

from tools import dev_extreme
from tools.permissions import ModelPermissions
from tools.serializers import DevExtremeGroupListSerializer


class DevExtremeViewSet(viewsets.ModelViewSet, mixins.ListModelMixin):
    permission_classes = [permissions.IsAuthenticated, ModelPermissions]
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
        if 'group' in self.request.GET:
            return DevExtremeGroupListSerializer
        return self.serializer_class

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        if self.get_exclude_fields():
            kwargs['exclude'] = self.get_exclude_fields()
        return serializer_class(*args, **kwargs)

    def get_serializer_context(self):
        context = super(DevExtremeViewSet, self).get_serializer_context()
        if self.totalCount:
            context.update({"totalCount": self.totalCount})
        return context

    # TODO: по-хорошему, поисковый фильтр нужно переложить на фронтенд
    def search_filter(self, queryset):
        return queryset

    def list_filter(self, queryset):
        return queryset

    def filter_queryset(self, queryset):
        if 'group' in self.request.GET:
            queryset = self.list_filter(queryset)
            queryset, self.totalCount = dev_extreme.populate_group_category(self.request.GET, queryset)
        elif 'searchValue' in self.request.GET:
            queryset = self.search_filter(queryset)
            searchValue = self.request.GET['searchValue'].strip('"').replace(',', ' ').split(' ')
            keywords = [x for x in searchValue if x]
            for keyword in keywords:
                q = Q()
                for field in self.lookup_fields:
                    q = q | Q(**{field + '__icontains': keyword})
                queryset = queryset.filter(q)
            self.totalCount = queryset.count()
            queryset = queryset[:10]

        else:
            queryset = self.list_filter(queryset)
            queryset, total_queryset, self.totalCount = dev_extreme.filtered_query(self.request.GET, queryset)
        return queryset

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = {'items': serializer.data,
                'totalCount': self.totalCount,
                'summary': [self.totalCount]}
        return Response(data)
