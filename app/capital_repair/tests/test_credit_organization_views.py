from mixer.backend.django import mixer
from rest_framework.test import APIClient

from capital_repair.models import CreditOrganization
from iggnpk.tests.base import BaseTest

endpoint_url = '/api/v1/cr/credit_organizations/'

class CreditOrganizationListViewSetTest(BaseTest):
    def test_returns_dict(self):
        bank  = mixer.blend(CreditOrganization)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.get(f'{endpoint_url}?filter=["id","=",{bank.id}]')
        self.assertTrue('items' in response.data)
        self.assertTrue('totalCount' in response.data)
        self.assertTrue('summary' in response.data)

    def test_allow_search_by_defined_fields(self):
        """Должен производиться поиск по следующим полям: ИНН, Наименование"""
        bank = mixer.blend(CreditOrganization, allow_to_select=True)
        mixer.blend(CreditOrganization, allow_to_select=True)
        mixer.blend(CreditOrganization, allow_to_select=True)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.get(f'{endpoint_url}?searchValue=%22{bank.name}%22&searchExpr=undefined')
        self.assertEqual(response.data['items'][0]['id'], bank.id)
        response = client.get(f'{endpoint_url}?searchValue=%22{bank.inn}%22&searchExpr=undefined')
        self.assertEqual(response.data['items'][0]['id'], bank.id)

class CreditOrganizationRetrieveViewSetTest(BaseTest):
    def test_returns_object(self):
        bank = mixer.blend(CreditOrganization, allow_to_select=True)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.get(f'{endpoint_url}{bank.id}/',)
        self.assertEqual(response.data['id'] ,bank.id)
        self.assertEqual(response.data['name'], bank.name)