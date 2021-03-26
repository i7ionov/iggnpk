import time

from django.test import override_settings

from dictionaries.models import User, Organization, House, Address, File, OrganizationType
from iggnpk.tests.base import BaseTest

from rest_framework.test import APIClient
from mixer.backend.django import mixer

endpoint_url = '/api/v1/dict/houses/'

class HousesListViewSetTest(BaseTest):
    def test_returns_dict(self):
        id = House.objects.first().id
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.get(f'{endpoint_url}?filter=["id","=",{id}]')
        self.assertTrue('items' in response.data)
        self.assertTrue('totalCount' in response.data)
        self.assertTrue('summary' in response.data)

    def test_search(self):
        addr = mixer.blend(Address)
        house = mixer.blend(House, number='unique house number', address=addr)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.get(
            f'{endpoint_url}?searchValue=%22{house.number}%22&searchExpr=%22number%22&take=10&skip=0&filter=["address_id","=",{addr.id}]')
        print(response.data)
        self.assertTrue('items' in response.data)
        self.assertTrue('totalCount' in response.data)
        self.assertTrue('summary' in response.data)