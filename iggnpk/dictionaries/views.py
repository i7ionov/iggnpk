from django.db.models import Q
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import User, House, Address, Organization, File
from .serializers import UserSerializer, HouseSerializer, AddressSerializer, OrganizationSerializer, FileSerializer
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from tools import dev_extreme


@api_view()
def is_org_is_not_exists(request):
    result = True
    if 'email' in request.GET:
        email = request.GET['email']
        if User.objects.filter(email=email).count() > 0:
            result = False
    elif 'inn' in request.GET:
        inn = request.GET['inn']
        if User.objects.filter(inn=inn).count() > 0:
            result = False
    elif 'ogrn' in request.GET:
        ogrn = request.GET['ogrn']
        if User.objects.filter(ogrn=ogrn).count() > 0:
            result = False
    else:
        return Response({"message": 'Электронная почта не указана'})
    return Response({"message": result})


class HouseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = House.objects.all()
    serializer_class = HouseSerializer

    def list(self, request):
        if 'group' in request.GET:
            d, total_count = dev_extreme.populate_group_category(request, House)
            data = {"totalCount": total_count, "items": d}
        else:
            queryset, total_count = dev_extreme.filtered_query(request, House)
            serializer = HouseSerializer(queryset, many=True)
            data = {'items': serializer.data, 'totalCount': total_count}
        return Response(data)

    def retrieve(self, request, pk=None):
        queryset = House.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = HouseSerializer(item)
        return Response(serializer.data)


class OrganizationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def list(self, request):
        if 'group' in request.GET:
            d, total_count = dev_extreme.populate_group_category(request, User)
            data = {"totalCount": total_count, "items": d}
        else:
            queryset, total_count = dev_extreme.filtered_query(request, User)
            serializer = self.serializer_class(queryset, many=True, fields=['id', 'name', 'inn'])
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


class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def list(self, request):
        if 'group' in request.GET:
            d, total_count = dev_extreme.populate_group_category(request, Address)
            data = {"totalCount": total_count, "items": d}
        else:
            queryset, total_count = dev_extreme.filtered_query(request, Address)
            serializer = AddressSerializer(queryset, many=True)
            data = {'items': serializer.data, 'totalCount': total_count}
        return Response(data)

    def retrieve(self, request, pk=None):
        queryset = Address.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = AddressSerializer(item)
        return Response(serializer.data)

    def search(self, request):
        if 'searchValue' in request.GET:
            searchValue = request.GET['searchValue'].strip('"').replace(',', ' ').split(' ')
            keywords = [x for x in searchValue if x]
            queryset = Address.objects.all()
            for keyword in keywords:
                queryset = queryset.filter(Q(area__icontains=keyword) | Q(city__icontains=keyword) | Q(street__icontains=keyword))
            serializer = AddressSerializer(queryset, many=True)
            data = {'items': serializer.data}
            return Response(data)
        else: return Response()


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = User.objects.all()
    parser_class = (FileUploadParser,)
    serializer_class = UserSerializer

    def me(self, request, pk=None):
        me = request.user
        serializer = self.serializer_class(me)
        return Response(serializer.data)


class FileViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = File.objects.all()
    serializer_class = FileSerializer
    parser_class = (FileUploadParser, MultiPartParser, FormParser,)

    def upload(self, request, format=None):
        if 'file' not in request.data:
            raise ParseError("Empty content")

        f = request.data['file']
        file = File()
        file.owner = self.request.user
        file.datafile.save(f.name, f, save=True)
        return Response(self.serializer_class(file).data, status=status.HTTP_201_CREATED)



