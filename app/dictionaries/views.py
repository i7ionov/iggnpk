import os
from django_sendfile import sendfile
from django.contrib.auth.models import Group
from django.core.files.storage import default_storage
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import permissions, status
from iggnpk import settings
from tools.service import ServiceException
from tools.viewsets import DevExtremeViewSet
from .models import User, House, Address, Organization, File, OrganizationType
from .serializers import UserSerializer, HouseSerializer, AddressSerializer, OrganizationSerializer, FileSerializer, \
    OrganizationTypeSerializer, GroupSerializer
from rest_framework.decorators import api_view, action
from rest_framework import viewsets
from django.core.mail import send_mail
from .services import HouseService, OrganizationService, AddressService, UserService
from .tasks import import_houses_from_register_of_KR


class HouseViewSet(DevExtremeViewSet):
    service = HouseService()
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    lookup_fields = ['number']
    parser_class = (FileUploadParser, MultiPartParser, FormParser,)

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
    service = OrganizationService()
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    lookup_fields = ['inn', 'name']


class AddressViewSet(DevExtremeViewSet):
    service = AddressService
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    lookup_fields = ['area', 'city', 'street']


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
    try:
        data = UserService().register(request.data)
        return Response(data)
    except ServiceException as e:
        return Response(e.errors, status=400)


class UserViewSet(DevExtremeViewSet):
    service = UserService()
    queryset = User.objects.all()
    serializer_class = UserSerializer


class FileViewSet(viewsets.ViewSet):
    permission_classes = []
    queryset = File.objects.all()
    serializer_class = FileSerializer
    parser_class = (FileUploadParser, MultiPartParser, FormParser,)

    def retrieve(self, request, *args, **kwargs):
        if 'pk' not in kwargs:
            return Response({'response': "Неверно указан id файла"}, status=400)
        file = File.objects.get(uuid=kwargs['pk'])
        return sendfile(request, file.datafile.name)

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