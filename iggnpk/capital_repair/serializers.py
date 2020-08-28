from rest_framework.relations import PrimaryKeyRelatedField

from dictionaries.models import File
from .models import CreditOrganization, Branch, Notify, NotifyStatus
from tools.dynamic_fields_model_serializer import DynamicFieldsModelSerializer
from dictionaries.serializers import OrganizationSerializer, HouseSerializer, FileSerializer
from rest_framework import serializers


class CreditOrganisationSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = CreditOrganization
        fields = '__all__'


class BranchSerializer(DynamicFieldsModelSerializer):
    credit_organization = CreditOrganisationSerializer()

    class Meta:
        model = Branch
        fields = '__all__'


class NotifyStatusSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = NotifyStatus
        fields = '__all__'


class NotifySerializer(DynamicFieldsModelSerializer):
    organization = OrganizationSerializer(required=False, read_only=True)
    bank = CreditOrganisationSerializer(required=False, read_only=True)
    house = HouseSerializer(required=False, read_only=True)
    files = FileSerializer(required=False, read_only=True, many=True)
    status = NotifyStatusSerializer(required=False, read_only=True)

    class Meta:
        model = Notify
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        exclude = kwargs.pop('exclude', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if exclude is not None:
            for field in exclude:
                self.fields.pop(field)
