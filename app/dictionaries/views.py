import os

from django.contrib.auth.models import Group
from django.core.files.storage import default_storage
from django.db.models import Q
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from iggnpk import settings
from tools.address_normalizer import normalize_number, normalize_street, normalize_city
from tools.replace_quotes import replace_quotes
from tools.serializer_tools import upd_foreign_key, upd_many_to_many
from tools.viewsets import DevExtremeViewSet
from .models import User, House, Address, Organization, File, OrganizationType
from .serializers import UserSerializer, HouseSerializer, AddressSerializer, OrganizationSerializer, FileSerializer, \
    OrganizationTypeSerializer, GroupSerializer
from rest_framework.decorators import api_view, action
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from tools import dev_extreme
from django.core.mail import send_mail

from .tasks import import_houses_from_register_of_KR


class HouseViewSet(DevExtremeViewSet):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    lookup_fields = ['number']
    parser_class = (FileUploadParser, MultiPartParser, FormParser,)

    def create(self, request, *args, **kwargs):
        item = self.serializer_class(data=request.data)
        item.is_valid()
        if item.is_valid():
            addr = Address.objects.get(id=request.data['address']['id'])
            item.save(address=addr, number=normalize_number(request.data['number']))
            return Response(item.data)
        else:
            return Response(item.errors, status=400)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        serializer = self.get_serializer_class()(instance=instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        addr = upd_foreign_key('address', data, instance, Address)
        serializer.save(address=addr, number=normalize_number(request.data['number']))
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def export_from_reg_program(self, request, *args, **kwargs):
        if 'files[]' not in request.data:
            raise ParseError("Empty content")

        f = request.data['files[]']
        path = default_storage.save('temp/kr.xlsx', f.file)
        path = os.path.join(settings.MEDIA_ROOT, path)
        user = UserSerializer(request.user)
        import_houses_from_register_of_KR.delay(path, user.data['email'])
        return Response({}, status=200)


class OrganizationTypeViewSet(DevExtremeViewSet):
    permission_classes = []
    queryset = OrganizationType.objects.all()
    serializer_class = OrganizationTypeSerializer
    lookup_fields = ['text']


class OrganizationViewSet(DevExtremeViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    lookup_fields = ['inn', 'name']

    def create(self, request, *args, **kwargs):
        item = self.serializer_class(data=request.data)
        item.is_valid()
        if item.is_valid():
            org_type = OrganizationType.objects.get(id=request.data['type']['id'])
            item.save(type=org_type, name=replace_quotes(request.data['name']))
            return Response(item.data)
        else:
            return Response(item.errors, status=400)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        serializer = self.get_serializer_class()(instance=instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        org_type = upd_foreign_key('type', data, instance, OrganizationType)
        serializer.save(type=org_type)
        return Response(serializer.data)


class AddressViewSet(DevExtremeViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    lookup_fields = ['area', 'city', 'street']

    def create(self, request, *args, **kwargs):
        item = self.serializer_class(data=request.data)
        item.is_valid()
        if item.is_valid():
            item.save(street=normalize_street(request.data['street']),
                        city=normalize_city(request.data['city']))
            return Response(item.data)
        else:
            return Response(item.errors, status=400)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        serializer = self.get_serializer_class()(instance=instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(street=normalize_street(request.data['street']),
                        city=normalize_city(request.data['city']))
        return Response(serializer.data)


class GroupViewSet(DevExtremeViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    queryset = Group.objects.all()
    serializer_class = GroupSerializer



@api_view(['GET'])
def me(request):
    me = request.user
    serializer = UserSerializer(me)
    return Response(serializer.data)


@api_view(['GET'])
def org_users_count(request):
    if 'inn' in request.GET:
        try:
            org = Organization.objects.get(inn=request.GET['inn'])
            return Response({"count": org.user_set.count()})
        except Organization.DoesNotExist:
            pass
    return Response({"count": 0})


@api_view(['GET'])
def is_email_already_used(request):
    if 'email' in request.GET:
        return Response({"result": User.objects.filter(email=request.GET['email']).count() > 0})
    return Response({"result": False})


@api_view(['GET'])
def is_username_already_used(request):
    if 'username' in request.GET:
        return Response({"result": User.objects.filter(username=request.GET['username']).count() > 0})
    return Response({"result": False})


@api_view(['POST'])
def register(request):
    item = UserSerializer(data=request.data)
    item.is_valid(raise_exception=True)
    if item.is_valid():
        if request.data['password'] != request.data['re_password']:
            return Response({'password': 'Пароли не совпадают'}, status=400)
        if 'organization' not in request.data:
            return Response({'organization': 'Не указана организация'}, status=400)
        if 'name' not in request.data['organization']:
            return Response({'organization': 'Не указано наименование организации'}, status=400)
        if 'inn' not in request.data['organization']:
            return Response({'organization': 'Не указан ИНН организации'}, status=400)
        if 'ogrn' not in request.data['organization']:
            return Response({'organization': 'Не указан ОГРН организации'}, status=400)
        if 'type' not in request.data['organization'] or 'id' not in request.data['organization']['type'] :
            return Response({'organization': 'Не указан тип организации'}, status=400)
        org, created = Organization.objects.get_or_create(inn=request.data['organization']['inn'])
        if created:
            org.name = request.data['organization']['name']
            org.ogrn = request.data['organization']['ogrn']
            org.type = OrganizationType.objects.get(id=request.data['organization']['type']['id'])
            org.save()
        User.objects.create_user(username=request.data['username'], organization=org,
                                 password=request.data['password'], email=request.data['email'])\
            .groups.add(Group.objects.get(name='Управляющие организации'))
        return Response(status=200)
    else:
        return Response(item.errors, status=400)


class UserViewSet(DevExtremeViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        item = self.serializer_class(data=request.data)
        item.is_valid()
        if item.is_valid():
            if request.data['password'] != request.data['re_password']:
                return Response({'password': 'Пароли не совпадают'}, status=400)
            if 'organization' not in request.data or 'id' not in request.data['organization']:
                return Response({'organization': 'Не выбрана организация'}, status=400)
            org = Organization.objects.get(id=request.data['organization']['id'])
            groups = upd_many_to_many('groups', request, None, Group)
            is_staff = Group.objects.get(name='Администраторы') in groups
            if 'is_active' not in request.data:
                is_active = False
            else:
                is_active = request.data['is_active']
            if len(groups) == 0:
                groups.append(Group.objects.get(name='Управляющие организации'))
            item.save(organization=org, groups=groups, is_active=is_active, is_staff=is_staff)
            user = User.objects.get(id=item.instance.id)
            user.set_password(request.data['password'])
            user.save()
            return Response(item.data)
        else:
            return Response(item.errors, status=400)

    def update(self, request, *args, **kwargs):
        if request.data['id'] != 1 and request.user.has_perm('dictionaries.change_user'):
            data = request.data
            instance = self.get_object()
            serializer = self.serializer_class(instance=instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            if 'password' in request.data:
                if request.data['password'] != request.data['re_password']:
                    return Response({'password': 'Пароли не совпадают'}, status=400)
                instance.set_password(request.data['password'])
            org = upd_foreign_key('organization', data, instance, Organization)
            groups = upd_many_to_many('groups', request, None, Group)
            is_staff = Group.objects.get(name='Администраторы') in groups
            serializer.save(organization=org, groups=groups, is_staff=is_staff)
            if 'sendmail' in request.GET and request.GET['sendmail'] == 'true':
                if serializer.data['is_active']:
                    message = 'активировна'
                else:
                    message = 'отключена'
                send_mail(
                    f'Учетная запись на портале iggnpk.ru {message}',
                    f'Учетная запись на портале iggnpk.ru {message}',
                    'noreply@iggnpk.ru',
                    [serializer.data['email']],
                    fail_silently=False,
                )
            return Response(serializer.data)
        return Response({'response': "У вас нет соответствующих прав"}, status=400)


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
        file.name = f.name
        file.datafile.save(f.name, f, save=True)
        return Response(self.serializer_class(file).data, status=status.HTTP_201_CREATED)


@api_view()
def send_message(request):
    send_mail(
        'Subject here',
        'Here is the message.',
        'noreply@iggnpk.com',
        ['i7ionov@gmail.com'],
        fail_silently=False,
    )
    return Response(status=200)