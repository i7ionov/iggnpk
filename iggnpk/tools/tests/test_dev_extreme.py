from dictionaries.models import Organization

from iggnpk.tests.base import BaseTest
from tools import dev_extreme


class FilteredQueryTest(BaseTest):
    def test_returns_tuple(self):
        request = self.factory.get('', {'title': 'new idea'})
        paged_qury, full_query, count = dev_extreme.filtered_query(request, Organization.objects.all())
        self.assertEqual(type(paged_qury), type(Organization.objects.all()))
        self.assertEqual(type(full_query), type(Organization.objects.all()))
        self.assertEqual(count, 25)

    def test_filter_single_item(self):
        """"[["id","=",1],"and",["!",["doc_number","=","+2664Л-1"]]]"""
        request = self.factory.get('/?filter=["id","=",1]')
        paged_qury, full_query, count = dev_extreme.filtered_query(request, Organization.objects.all())
        self.assertQuerysetEqual(full_query, [repr(r) for r in Organization.objects.filter(id=1)])
        self.assertEqual(count, 1)
        """http://127.0.0.1:8000/api/v1/cr/notifies/?skip=0&take=5&sort=[{"selector":"id","desc":false}]&filter=[["id","=",1],"and",["house.address.area","contains","q"]]&totalSummary=[{"selector":"status.text","summaryType":"count"},{"selector":"monthly_contribution_amount","summaryType":"avg"},{"selector":"monthly_contribution_amount","summaryType":"sum"}]&orderby=id"""