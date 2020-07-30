from django.db.models import Q
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import User, House, Address, Organization, File, OrganizationType
from .serializers import UserSerializer, HouseSerializer, AddressSerializer, OrganizationSerializer, FileSerializer, \
    OrganizationTypeSerializer
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from tools import dev_extreme


@api_view()
def org_users_count(request):
    if 'inn' in request.GET:
        try:
            org = Organization.objects.get(inn=request.GET['inn'])
            return Response({"count": org.user_set.count()})
        except Organization.DoesNotExist:
            pass
    return Response({"count": 0})


@api_view()
def is_email_already_used(request):
    if 'email' in request.GET:
        try:
            return Response({"result": User.objects.filter(email=request.GET['email']).count() > 0})
        except Organization.DoesNotExist:
            pass
    return Response({"result": False})


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
    permission_classes = []
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
    def types(self, request):
        data = OrganizationTypeSerializer(OrganizationType.objects.all(), many=True)

        return Response(data.data)


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
            queryset = queryset[:10]
            serializer = AddressSerializer(queryset, many=True)
            data = {'items': serializer.data}
            return Response(data)
        else: return Response()


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = []
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def me(self, request, pk=None):
        me = request.user
        serializer = self.serializer_class(me)
        return Response(serializer.data)

    def create(self, request, pk=None):
        item = self.serializer_class(data=request.data)
        item.is_valid(raise_exception=True)

        if item.is_valid():
            if request.data['password'] != request.data['re_password']:
                return Response({'password': 'Пароли не совпадают'}, status=400)
            org, created = Organization.objects.get_or_create(inn=request.data['organization']['inn'])
            print(request.data)
            if created:
                org.name = request.data['organization']['name']
                org.ogrn = request.data['organization']['ogrn']
                org.type = OrganizationType.objects.get(id=request.data['organization']['type']['id'])
            User.objects.create_user(username=request.data['username'], organization=org, password=request.data['password'], email=request.data['email'])
            return Response(status=200)
        else:
            return Response(item.errors, status=400)


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



