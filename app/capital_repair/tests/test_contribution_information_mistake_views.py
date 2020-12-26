from mixer.backend.django import mixer
from rest_framework.test import APIClient

from capital_repair.models import ContributionsInformationMistake
from iggnpk.tests.base import BaseTest

endpoint_url = '/api/v1/cr/contrib_info_mistake/'

class ContributionsInformationMistakeListViewSetTest(BaseTest):
    def test_returns_dict(self):
        mistake = mixer.blend(ContributionsInformationMistake)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.get(f'{endpoint_url}?filter=["id","=",{mistake.id}]')
        self.assertTrue('items' in response.data)
        self.assertTrue('totalCount' in response.data)
        self.assertTrue('summary' in response.data)

    def test_allow_search_by_defined_fields(self):
        """Должен производиться поиск по следующим полям: Текст"""
        mistake = mixer.blend(ContributionsInformationMistake)
        mixer.blend(ContributionsInformationMistake)
        mixer.blend(ContributionsInformationMistake)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.get(f'{endpoint_url}?searchValue=%22{mistake.text}%22&searchExpr=undefined')
        self.assertEqual(response.data['items'][0]['id'], mistake.id)


class ContributionsInformationMistakeRetrieveViewSetTest(BaseTest):
    def test_returns_object(self):
        mistake = mixer.blend(ContributionsInformationMistake)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.get(f'{endpoint_url}{mistake.id}/',)
        self.assertEqual(response.data['id'] ,mistake.id)
        self.assertEqual(response.data['text'], mistake.text)