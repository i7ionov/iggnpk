from django.contrib.auth import authenticate
from capital_repair.models import Notify
from capital_repair.views import NotifiesViewSet
from dictionaries.models import User, Organization, House, Address
from iggnpk.tests.base import BaseTest

from rest_framework.test import APIClient
from mixer.backend.django import mixer


class NotifiesListViewSetTest(BaseTest):
    def test_returns_dict(self):
        id = Notify.objects.first().id
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.get(f'/api/v1/cr/notifies/?filter=["id","=",{id}]')
        self.assertTrue('items' in response.data)
        self.assertTrue('totalCount' in response.data)
        self.assertTrue('summary' in response.data)

    def test_needs_authentification(self):
        client = APIClient()
        response = client.get(f'/api/v1/cr/notifies/')
        self.assertEqual(response.status_code, 401)

    def test_uk_can_see_its_own_notifies(self):
        """Управляющие организации не должны видеть уведомления других"""
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.get(f'/api/v1/cr/notifies/')
        self.assertEqual(response.data['totalCount'], Notify.objects.filter(organization=self.uk.organization).count())
        for n in response.data['items']:
            self.assertEqual(n['organization']['id'], self.uk.organization.id,
                             msg=f"Уведомление с id {n['id']} принадлежит организации {n['organization']['id']}, хотя должно {self.uk.organization.id}")
        # в том числе через фильтрацию
        other_org = mixer.blend(Organization)
        other_notify = mixer.blend(Notify, organization=other_org)
        response = client.get(f'/api/v1/cr/notifies/?filter=["id","=",{other_notify.id}]')
        self.assertEqual(response.data['totalCount'], 0, msg='УК не должна видеть не свои уведомления даже после фильтрации')
        self.assertEqual(len(response.data['items']), 0, msg='УК не должна видеть не свои уведомления даже после фильтрации')

    def test_uk_cant_see_additional_fields(self):
        """Управляющие организации не должны видеть дополнительные поля"""
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.get(f'/api/v1/cr/notifies/')
        for field in NotifiesViewSet.additional_fields:
            self.assertTrue(field in response.data['items'][0], msg=f'{field} должно выдаваться администратору')
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        mixer.blend(Notify, organization=self.uk.organization)
        response = client.get(f'/api/v1/cr/notifies/')
        for field in NotifiesViewSet.additional_fields:
            self.assertTrue(field not in response.data['items'][0], msg=f'{field} не должно выдаваться УК')


class NotifiesSearchViewSetTest(BaseTest):
    def test_returns_dict(self):
        notify = mixer.blend(Notify, organization=self.uk.organization, status_id=3)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.get(f'/api/v1/cr/notifies/search/?searchValue=%22%22&searchExpr=undefined')
        self.assertTrue('items' in response.data)

    def test_needs_authentification(self):
        client = APIClient()
        response = client.get(f'/api/v1/cr/notifies/search/?searchValue=%22%22&searchExpr=undefined')
        self.assertEqual(response.status_code, 401)

    def test_uk_can_see_its_own_notifies(self):
        """Управляющие организации не должны видеть уведомления других"""
        notify = mixer.blend(Notify, organization=self.uk.organization, status_id=3)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.get(f'/api/v1/cr/notifies/search/?searchValue=%22%22&searchExpr=undefined')
        for n in response.data['items']:
            self.assertEqual(n['organization']['id'], self.uk.organization.id,
                             msg=f"Уведомление с id {n['id']} принадлежит организации {n['organization']['id']}, хотя должно {self.uk.organization.id}")
        # в том числе через фильтрацию
        other_org = mixer.blend(Organization)
        other_notify = mixer.blend(Notify, organization=other_org, status_id=3)
        response = client.get(f'/api/v1/cr/notifies/search/?searchValue=%22{other_notify.id}%22&searchExpr=undefined')
        self.assertEqual(len(response.data['items']), 0, msg='УК не должна видеть не свои уведомления даже после фильтрации')

    def test_uk_cant_see_additional_fields(self):
        """Управляющие организации не должны видеть дополнительные поля"""
        notify = mixer.blend(Notify, organization=self.uk.organization, status_id=3)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.get(f'/api/v1/cr/notifies/search/?searchValue=%22{notify.id}%22&searchExpr=undefined')
        for field in NotifiesViewSet.additional_fields:
            self.assertTrue(field in response.data['items'][0], msg=f'{field} должно выдаваться администратору')
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        mixer.blend(Notify, organization=self.uk.organization)
        response = client.get(f'/api/v1/cr/notifies/search/?searchValue=%22{notify.id}%22&searchExpr=undefined')
        for field in NotifiesViewSet.additional_fields:
            self.assertTrue(field not in response.data['items'][0], msg=f'{field} не должно выдаваться УК')

    def test_allows_search_by_defined_fields(self):
        """Должен производиться поиск по следующим полям: id, номер счета, поля адреса"""
        house = mixer.blend(House,address=mixer.blend(Address, area='area', city='city',street='street'), number='number')
        notify = mixer.blend(Notify, organization=self.uk.organization, status_id=3, house=house, account_number='account_number')
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.get(f'/api/v1/cr/notifies/search/?searchValue=%22account_number%22&searchExpr=undefined')
        self.assertEqual(response.data['items'][0]['id'], notify.id)
        response = client.get(f'/api/v1/cr/notifies/search/?searchValue=%22area%22&searchExpr=undefined')
        self.assertEqual(response.data['items'][0]['id'], notify.id)
        response = client.get(f'/api/v1/cr/notifies/search/?searchValue=%22city%22&searchExpr=undefined')
        self.assertEqual(response.data['items'][0]['id'], notify.id)
        response = client.get(f'/api/v1/cr/notifies/search/?searchValue=%22street%22&searchExpr=undefined')
        self.assertEqual(response.data['items'][0]['id'], notify.id)
        response = client.get(f'/api/v1/cr/notifies/search/?searchValue=%22number%22&searchExpr=undefined')
        self.assertEqual(response.data['items'][0]['id'], notify.id)