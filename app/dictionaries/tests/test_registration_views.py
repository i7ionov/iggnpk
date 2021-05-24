import time

from django.contrib.auth.models import Group
from django.test import override_settings

from dictionaries.models import User, Organization, House, Address, File, OrganizationType
from iggnpk.tests.base import BaseTest

from rest_framework.test import APIClient
from mixer.backend.django import mixer

endpoint_url = '/api/v1/dict/users/'

class RegisterTest(BaseTest):
    def setUp(self):
        super(RegisterTest, self).setUp()
        self.org = mixer.blend(Organization)
        self.org_type = mixer.blend(OrganizationType)
        self.g1 = Group.objects.get(name='Управляющие организации')
        self.g2 = Group.objects.get(name='Администраторы')
        self.data = {
            "id": 0,
            'is_active': True,
            "groups": [{"id": self.g2.id}],
            "email": 'test@email.ru',
            "username": '123',
            "password": '123',
            "re_password": '123',
            "organization": {'name': 'org name', 'inn': 'org inn', 'ogrn': 'org ogrn', 'type':{'id': self.org_type.id}}
        }
    def test_user_registration(self):
        client = APIClient()
        response = client.post(f'{endpoint_url}register/', self.data, format='json')
        user = User.objects.last()
        org = Organization.objects.last()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.username, '123')
        self.assertEqual(user.is_active, False)
        self.assertEqual(user.organization.id, org.id)
        self.assertTrue(user.check_password('123'))
        self.assertEqual({self.g1}, set(user.groups.all()))

    def test_requires_organization_name(self):
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        data = dict(self.data)
        data['organization'].pop('name')
        response = client.post(f'{endpoint_url}register/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_requires_organization_inn(self):
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        data = dict(self.data)
        data['organization'].pop('inn')
        response = client.post(f'{endpoint_url}register/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_requires_organization_type(self):
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        data = dict(self.data)
        data['organization'].pop('type')
        response = client.post(f'{endpoint_url}register/', data, format='json')
        self.assertEqual(response.status_code, 400)

