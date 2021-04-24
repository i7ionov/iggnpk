from rest_framework import serializers


class CrReportSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    mkd_in_reg_program = serializers.DictField()
    total_area = serializers.DictField()
    last_year_funds_spent = serializers.DictField()
    assessed_contributions_total = serializers.DictField()
    received_contributions_total = serializers.DictField()
    level_of_fundraising_total = serializers.DictField()
    assessed_contributions_current = serializers.DictField()
    received_contributions_current = serializers.DictField()
    level_of_fundraising_current = serializers.DictField()
    total_debt = serializers.DictField()
    fund_balance_total = serializers.DictField()
    fund_balance_total_and_current = serializers.DictField()

