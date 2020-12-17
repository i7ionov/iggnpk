from django.db.models import Avg

from dictionaries.models import Organization
from capital_repair.models import ContributionsInformation, Notify

from iggnpk.tests.base import BaseTest
from tools import dev_extreme


class FilteredQueryTest(BaseTest):
    def test_returns_tuple(self):
        request = self.factory.get('', {'title': 'new idea'})
        paged_qury, full_query, count = dev_extreme.filtered_query(request.GET, Organization.objects.all())
        self.assertEqual(type(paged_qury), type(Organization.objects.all()))
        self.assertEqual(type(full_query), type(Organization.objects.all()))
        self.assertEqual(count, 25)

    def test_filter_single_item(self):
        """"[["id","=",1]"""
        id = Organization.objects.first().id
        request = self.factory.get(f'/?filter=["id","=",{id}]')
        paged_qury, full_query, count = dev_extreme.filtered_query(request.GET, Organization.objects.all())
        self.assertQuerysetEqual(full_query, [repr(r) for r in Organization.objects.filter(id=id)])
        self.assertEqual(count, 1)
        """http://127.0.0.1:8000/api/v1/cr/notifies/?skip=0&take=5&sort=[{"selector":"id","desc":false}]&filter=[["id","=",1],"and",["house.address.area","contains","q"]]&totalSummary=[{"selector":"status.text","summaryType":"count"},{"selector":"monthly_contribution_amount","summaryType":"avg"},{"selector":"monthly_contribution_amount","summaryType":"sum"}]&orderby=id"""

    def test_query_can_aggregate(self):
        request = self.factory.get('/?filter=["id","=",1]')
        paged_qury, full_query, count = dev_extreme.filtered_query(request.GET, ContributionsInformation.objects.all())
        full_query.aggregate(Avg('received_contributions_total'))

    def test_distincted_by_id(self):
        request = self.factory.get('/?filter=[["mistakes__text","contains","Ошибка 1"], "or", ["mistakes__text","contains","Ошибка 2"]]')
        paged_qury, full_query, count = dev_extreme.filtered_query(request.GET, ContributionsInformation.objects.all())
        self.assertEqual(full_query.count(), 2)
