import time

from django.test import override_settings

from dictionaries.models import User, Organization, House, Address, File, OrganizationType
from iggnpk.tests.base import BaseTest

from rest_framework.test import APIClient
from mixer.backend.django import mixer

endpoint_url = '/api/v1/dict/organizations/'


class OrganizationListViewSetTest(BaseTest):
    def test_returns_dict(self):
        id = Organization.objects.first().id
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.get(f'{endpoint_url}?filter=["id","=",{id}]')
        self.assertTrue('items' in response.data)
        self.assertTrue('totalCount' in response.data)
        self.assertTrue('summary' in response.data)

    def test_needs_authentification(self):
        client = APIClient()
        response = client.get(f'{endpoint_url}')
        self.assertEqual(response.status_code, 401)

    def test_needs_permission(self):
        self.uk.groups.set([])
        self.uk.save()
        self.uk = User.objects.get(id=self.uk.id)  # обновление закэшированых разрешений
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.get(f'{endpoint_url}')
        self.assertEqual(response.status_code, 403)


class OrganizationsCreateViewSetTest(BaseTest):
    def test_creates_object(self):
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        org_type = mixer.blend(OrganizationType)
        response = client.post(f'{endpoint_url}', {
            "id": 0,
            "inn": 'test inn',
            "ogrn": 'test ogrn',
            "name": 'test name',
            "type": {"id": org_type.id}
        }, format='json')
        org = Organization.objects.last()
        self.assertEqual(org.inn, 'test inn')
        self.assertEqual(org.ogrn, 'test ogrn')
        self.assertEqual(org.name, 'test name')
        self.assertEqual(org.type, org_type)
