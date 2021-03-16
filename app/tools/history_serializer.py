from rest_framework import serializers


class HistorySerializer(serializers.Serializer):
    pk = serializers.CharField()
    history_date = serializers.DateTimeField()
    history_type = serializers.CharField(max_length=1)
    history_user = serializers.CharField(max_length=100)
    history_user_id = serializers.IntegerField()
    delta = serializers.SerializerMethodField()

    def __init__(self, **kwargs):
        self.model = kwargs['instance'].model
        super().__init__(**kwargs)

    def get_delta(self, obj):
        result = []
        if obj.prev_record:
            for change in obj.diff_against(obj.prev_record).changes:
                if change.new or change.old:
                    result.append({
                        'field':change.field,
                        'field_verbose':self.model._meta.get_field(change.field).verbose_name,
                        'new':change.new,
                        'old':change.old})
        return result