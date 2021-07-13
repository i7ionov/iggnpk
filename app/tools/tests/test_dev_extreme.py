from django.db.models import Avg, Q
from mixer.backend.django import mixer

from dictionaries.models import Organization
from capital_repair.models import ContributionsInformation, Notify

from iggnpk.tests.base import BaseTest
from tools import dev_extreme
from tools.dev_extreme import build_q_object


class FilteredQueryTest(BaseTest):
    def test_returns_tuple(self):
        request = self.factory.get('', {'title': 'new idea'})
        paged_qury, full_query, count = dev_extreme.filtered_query(request.GET, Organization.objects.all())
        self.assertEqual(type(paged_qury), type(Organization.objects.all()))
        self.assertEqual(type(full_query), type(Organization.objects.all()))
        self.assertEqual(count, Organization.objects.all().count())

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
        request = self.factory.get(
            '/?filter=[["mistakes__text","contains","Ошибка 1"], "or", ["mistakes__text","contains","Ошибка 2"]]')
        paged_qury, full_query, count = dev_extreme.filtered_query(request.GET, ContributionsInformation.objects.all())
        self.assertEqual(full_query.count(), 2)

    def test_cut_dates_with_time(self):
        contrib = mixer.blend(ContributionsInformation, date='2020-01-01')
        request = self.factory.get('/?filter=["date","=","2020-01-01T19:00:00.000Z"]')
        paged_qury, full_query, count = dev_extreme.filtered_query(request.GET, ContributionsInformation.objects.all())
        self.assertGreater(full_query.count(), 0)


class BuildQObjectTest(BaseTest):
    def test_accept_contains(self):
        filter_request = ["id", "=", 1]
        self.assertEqual(Q(**{'id': 1}), build_q_object(filter_request, Organization))

    def test_accept_lt(self):
        filter_request = ["id", "<", 1]
        self.assertEqual(Q(**{'id__lt': 1}),  build_q_object(filter_request, Organization))

    def test_accept_lte(self):
        filter_request = ["id", "<=", 1]
        self.assertEqual(Q(**{'id__lte': 1}),  build_q_object(filter_request, Organization))

    def test_accept_gt(self):
        filter_request = ["id", ">", 1]
        self.assertEqual(Q(**{'id__gt': 1}),  build_q_object(filter_request, Organization))

    def test_accept_gte(self):
        filter_request = ["id", ">=", 1]
        self.assertEqual(Q(**{'id__gte': 1}),  build_q_object(filter_request, Organization))

    def test_accept_ne(self):
        filter_request = ["id", "<>", 1]
        self.assertEqual(Q(**{'id__ne': 1}),  build_q_object(filter_request, Organization))

    def test_not_null_date(self):
        filter_request = ["date", "<>", None]
        self.assertEqual(Q(**{'date__isnull': False}),  build_q_object(filter_request, ContributionsInformation))

    def test_not_blank_date(self):
        filter_request = ["date", "<>", '']
        self.assertEqual(None,  build_q_object(filter_request, ContributionsInformation))

    def test_accept_complicated_filter(self):
        filter_request = [
            ["id", "=", 1],
            "and",
            ["!", ["comment", "=", "2664Л-1"]],
            "and",
            [
                [
                    ["date", ">=", "2015/09/29"],
                    "and",
                    ["date", "<", "2015/09/30"]
                ],
                "or",
                [
                    ["date", ">=", "2017/01/01"],
                    "and",
                    ["date", "<", "2018/01/01"]
                ]
            ]
        ]
        q = Q(**{'id': 1}) & \
            ~Q(**{'comment': '2664Л-1'}) & \
            (
                (
                        Q(**{'date__gte': '2015-09-29'}) &
                        Q(**{'date__lt': '2015-09-30'})
                ) |
                (
                        Q(**{'date__gte': '2017-01-01'}) &
                        Q(**{'date__lt': '2018-01-01'})
                )
            )
        self.assertEqual(q,  build_q_object(filter_request, ContributionsInformation))
