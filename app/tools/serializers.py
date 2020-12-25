from rest_framework import serializers


class DevExtremeListSerializer(serializers.ListSerializer):
    @property
    def data(self):
        ret = serializers.BaseSerializer.data.fget(self)
        return serializers.ReturnDict(ret, serializer=self)
    def to_representation(self, instance):
        if 'totalCount' in self.context:
            totalCount = self.context['totalCount']
        else:
            totalCount = 0
        representation = {'items': super().to_representation(instance), 'totalCount': totalCount, 'summary':'self.summary'}
        return representation


class DevExtremeGroupListSerializer(serializers.Serializer):

    def to_representation(self, instance):
        representation = instance
        return representation

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        kwargs.pop('exclude', None)
        super(serializers.Serializer, self).__init__(*args, **kwargs)

    class Meta:
        list_serializer_class = DevExtremeListSerializer