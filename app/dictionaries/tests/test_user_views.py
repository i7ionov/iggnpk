import time

from django.contrib.auth.models import Group
from django.test import override_settings

from dictionaries.models import User, Organization, House, Address, File, OrganizationType
from iggnpk.tests.base import BaseTest

from rest_framework.test import APIClient
from mixer.backend.django import mixer

endpoint_url = '/api/v1/dict/users/'


class UserListViewSetTest(BaseTest):
    def test_returns_dict(self):
        id = User.objects.first().id
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


class UserCreateViewSetTest(BaseTest):
    def setUp(self):
        super(UserCreateViewSetTest, self).setUp()
        self.org = mixer.blend(Organization)
        self.org_type = mixer.blend(OrganizationType)
        self.g1 = Group.objects.get(name='Управляющие организации')
        self.g2 = Group.objects.get(name='Администраторы')
        self.data = {
            "id": 0,
            'is_active': True,
            "groups": [{"id": self.g1.id},{"id": self.g2.id}],
            "username": '123',
            "password": '123',
            "re_password": '123',
            "organization": {"id": self.org.id}
        }

    def test_creates_object(self):
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        data = dict(self.data)
        response = client.post(f'{endpoint_url}', data, format='json')
        user = User.objects.last()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.username, '123')
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.organization.id, self.org.id)
        self.assertTrue(user.check_password('123'))
        self.assertEqual({self.g1, self.g2}, set(user.groups.all()))

    def test_requires_organization(self):
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        data = dict(self.data)
        data.pop('organization')
        response = client.post(f'{endpoint_url}', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_requires_passwords(self):
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        data = dict(self.data)
        data['re_password'] = 'another password'
        response = client.post(f'{endpoint_url}', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_set_UK_group_by_default(self):
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        data = dict(self.data)
        data.pop('groups')
        response = client.post(f'{endpoint_url}', data, format='json')
        user = User.objects.last()
        self.assertEqual({self.g1}, set(user.groups.all()))

    def test_needs_authentification(self):
        client = APIClient()
        data = dict(self.data)
        response = client.post(f'{endpoint_url}', data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_needs_permission(self):
        self.uk.groups.set([])
        self.uk.save()
        self.uk = User.objects.get(id=self.uk.id)  # обновление закэшированых разрешений
        data = dict(self.data)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.post(f'{endpoint_url}', data, format='json')
        self.assertEqual(response.status_code, 403)

class UserUpdateViewSetTest(BaseTest):
    def setUp(self):
        super(UserUpdateViewSetTest, self).setUp()
        self.org = mixer.blend(Organization)
        self.new_org = mixer.blend(Organization)
        self.g1 = Group.objects.get(name='Управляющие организации')
        self.g2 = Group.objects.get(name='Администраторы')
        self.user = mixer.blend(User, organization=self.org, groups=[self.g1])
        self.data = {
            "id": 0,
            'is_active': True,
            "groups": [{"id": self.g2.id},{"id": self.g1.id}],
            "username": '321',
            "password": '321',
            "re_password": '321',
            "organization": {"id": self.new_org.id},
        }

    def test_updates_object(self):
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        data = dict(self.data)
        response = client.patch(f'{endpoint_url}{self.user.id}/', data, format='json')
        user = User.objects.get(id=self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.username, '321')
        self.assertEqual(user.organization.id, self.new_org.id)
        self.assertTrue(user.check_password('321'))
        self.assertEqual({self.g1, self.g2}, set(user.groups.all()))

    def test_needs_authentification(self):
        client = APIClient()
        data = dict(self.data)
        response = client.patch(f'{endpoint_url}{self.user.id}/', data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_needs_permission(self):
        self.uk.groups.set([])
        self.uk.save()
        self.uk = User.objects.get(id=self.uk.id)  # обновление закэшированых разрешений
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        data = dict(self.data)
        response = client.patch(f'{endpoint_url}{self.user.id}/', data, format='json')
        self.assertEqual(response.status_code, 403)