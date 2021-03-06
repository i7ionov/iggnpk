from django.contrib.auth.models import Permission

from .models import User, House, Address, Organization, File, OrganizationType
from rest_framework import serializers
from tools.dynamic_fields_model_serializer import DynamicFieldsModelSerializer


class OrganizationTypeSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = OrganizationType
        fields = '__all__'


class OrganizationSerializer(DynamicFieldsModelSerializer):
    type = OrganizationTypeSerializer(required=False)
    class Meta:
        model = Organization
        fields = '__all__'


class AddressSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class HouseSerializer(DynamicFieldsModelSerializer):
    address = AddressSerializer()
    organization = OrganizationSerializer()

    class Meta:
        model = House
        fields = '__all__'


class PermissionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'codename')


class UserSerializer(DynamicFieldsModelSerializer):
    """Сериализация пользователя"""
    groups = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    organization = OrganizationSerializer(read_only=True)
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "groups", "organization", "permissions", "is_active")


class FileSerializer(DynamicFieldsModelSerializer):
    owner = serializers.SlugRelatedField(
        read_only=True,
        slug_field='id'
    )
    datafile = serializers.FileField(required=False,allow_empty_file=True)
    size = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = '__all__'
        read_only_fields = ('created', 'datafile', 'owner', 'size', 'name')

    def get_size(self, obj):
        try:
            return obj.datafile.size
        except (FileNotFoundError, ValueError):
            return None

