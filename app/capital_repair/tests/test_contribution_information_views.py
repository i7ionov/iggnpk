import datetime

from django.test import override_settings

from capital_repair.models import Notify, CreditOrganization, ContributionsInformation, ContributionsInformationMistake
from capital_repair.views import NotifiesViewSet, ContributionsInformationViewSet
from dictionaries.models import User, Organization, House, Address, File
from iggnpk.tests.base import BaseTest

from rest_framework.test import APIClient
from mixer.backend.django import mixer

endpoint_url = '/api/v1/cr/contrib_info/'


class ContribInfoListViewSetTest(BaseTest):
    def test_returns_dict(self):
        contrib = mixer.blend(ContributionsInformation)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.get(f'{endpoint_url}?filter=["id","=",{contrib.id}]')
        self.assertTrue('items' in response.data)
        self.assertTrue('totalCount' in response.data)
        self.assertTrue('summary' in response.data)

    def test_uk_can_see_its_own_contribs(self):
        """Управляющие организации не должны видеть взносы других"""
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.get(f'{endpoint_url}')
        self.assertEqual(response.data['totalCount'],
                         ContributionsInformation.objects.filter(notify__organization=self.uk.organization).count())
        for n in response.data['items']:
            self.assertEqual(n['notify']['organization']['id'], self.uk.organization.id,
                             msg=f"Взносы с id {n['id']} принадлежит организации {n['notify']['organization']['id']}, хотя должно {self.uk.organization.id}")
        # в том числе через фильтрацию
        other_org = mixer.blend(Organization)
        other_notify = mixer.blend(Notify, organization=other_org)
        other_contrib = mixer.blend(ContributionsInformation, notify=other_notify)
        response = client.get(f'{endpoint_url}?filter=["id","=",{other_contrib.id}]')
        self.assertEqual(response.data['totalCount'], 0,
                         msg='УК не должна видеть не свои взносы даже после фильтрации')
        self.assertEqual(len(response.data['items']), 0,
                         msg='УК не должна видеть не свои взносы даже после фильтрации')
        # администратор должен видеть все
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.get(f'{endpoint_url}?filter=["id","=",{other_contrib.id}]')
        self.assertEqual(response.data['totalCount'], 1,
                         msg='Администратор должнен видеть все уведомления')
        self.assertEqual(len(response.data['items']), 1,
                         msg='Администратор должнен видеть все уведомления')
        response = client.get(f'{endpoint_url}')
        self.assertEqual(response.data['totalCount'], ContributionsInformation.objects.all().count())

    def test_uk_cant_see_additional_fields(self):
        """Управляющие организации не должны видеть дополнительные поля"""
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.get(f'{endpoint_url}')
        for field in ContributionsInformationViewSet.additional_fields:
            self.assertTrue(field in response.data['items'][0], msg=f'{field} должно выдаваться администратору')
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        mixer.blend(ContributionsInformation, notify=mixer.blend(Notify, organization=self.uk.organization))
        response = client.get(f'{endpoint_url}')
        for field in ContributionsInformationViewSet.additional_fields:
            self.assertTrue(field not in response.data['items'][0], msg=f'{field} не должно выдаваться УК')

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


class ContribInfoCreateViewSetTest(BaseTest):
    def test_creates_object(self):
        notify = mixer.blend(Notify, organization=self.admin.organization)
        m1 = mixer.blend(ContributionsInformationMistake)
        m2 = mixer.blend(ContributionsInformationMistake)
        file = mixer.blend(File, owner=mixer.SELECT)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        json_data = {
            "id": 0,
            "notify": {"id": notify.id},
            "status": {"id": 1},
            "files": [{"id": file.id}],
            "mistakes": [{"id": m1.id}, {"id": m2.id}],
            "date": "2020-09-23",
            "assessed_contributions_total": "11",
            "assessed_contributions_current": "22",
            "received_contributions_total": "33",
            "received_contributions_current": "44",
            "delta_total": "55",
            "funds_spent": "12",
            "credit": "23",
            "funds_on_special_deposit": "34",
            "fund_balance": "66",
            "comment": "45",
            "comment2": "56"
        }
        response = client.post(f'{endpoint_url}', json_data, format='json')
        contrib = ContributionsInformation.objects.last()
        self.assertEqual(response.data['id'], contrib.id)
        self.assertEqual(contrib.status.id, 1)
        self.assertEqual(contrib.notify, notify)
        self.assertEqual([m1, m2], list(contrib.mistakes.all()))
        self.assertEqual([file], list(contrib.files.all()))
        self.assertEqual(contrib.assessed_contributions_total, 11)
        self.assertEqual(contrib.assessed_contributions_current, 22)
        self.assertEqual(contrib.received_contributions_total, 33)
        self.assertEqual(contrib.received_contributions_current, 44)
        self.assertEqual(contrib.delta_total, 55)
        self.assertEqual(contrib.funds_spent, 12)
        self.assertEqual(contrib.credit, 23)
        self.assertEqual(contrib.funds_on_special_deposit, 34)
        self.assertEqual(contrib.fund_balance, 66)
        self.assertEqual(contrib.comment, '45')
        self.assertEqual(contrib.comment2, '56')

    def test_does_not_allow_status_more_than_2(self):
        previous_contrib = mixer.blend(ContributionsInformation)
        notify = mixer.blend(Notify, organization=self.uk.organization)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        json_data = {
            "id": 0,
            "notify": {"id": notify.id},
            "status": {"id": 3},
            "files": [],
            "mistakes": [],
        }
        response = client.post(f'{endpoint_url}', json_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue(previous_contrib, ContributionsInformation.objects.last())

    def test_does_not_allow_save_uk_some_fields(self):
        notify = mixer.blend(Notify, organization=self.uk.organization)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        m1 = mixer.blend(ContributionsInformationMistake)
        m2 = mixer.blend(ContributionsInformationMistake)
        json_data = {
            "id": 0,
            "notify": {"id": notify.id},
            "status": {"id": 1},
            "files": [],
            "mistakes": [{"id": m1.id}, {"id": m2.id}],
        }
        for field in ContributionsInformationViewSet.additional_fields:
            json_data[field] = field
        response = client.post(f'{endpoint_url}', json_data, format='json')
        contrib = ContributionsInformation.objects.last()
        self.assertEqual(datetime.datetime.strptime(response.data['date'], '%Y-%m-%d').date(), datetime.date.today(),
                         msg='Должна записаться текущая дата')
        self.assertEqual(contrib.mistakes.count(), 0)
        for field in ContributionsInformationViewSet.additional_fields:
            self.assertTrue(field not in response.data, msg=f'{field} не должно выдаваться УК')
            self.assertEqual(contrib.__getattribute__(field), None, msg=f'{field} должно было остаться пустым')

    def test_uk_cant_set_not_its_own_notify(self):
        previous_contrib = mixer.blend(ContributionsInformation)
        notify = mixer.blend(Notify, organization=self.admin.organization)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        json_data = {
            "id": 0,
            "notify": {"id": notify.id},
            "status": {"id": 1},
            "files": [],
            "mistakes": [],
        }
        response = client.post(f'{endpoint_url}', json_data, format='json')
        self.assertTrue(response.status_code, 400)
        self.assertTrue(previous_contrib, ContributionsInformation.objects.last())

    def test_admin_can_set_not_its_own_notify(self):
        notify = mixer.blend(Notify, organization=self.uk.organization)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        json_data = {
            "id": 0,
            "notify": {"id": notify.id},
            "status": {"id": 1},
            "files": [],
            "mistakes": []
        }
        response = client.post(f'{endpoint_url}', json_data, format='json')
        self.assertTrue(response.status_code, 200)
        self.assertTrue(response.data['id'], ContributionsInformation.objects.last())

    def test_needs_authentification(self):
        client = APIClient()
        response = client.post(f'{endpoint_url}', {})
        self.assertEqual(response.status_code, 401)

    def test_needs_permission(self):
        self.uk.groups.set([])
        self.uk.save()
        self.uk = User.objects.get(id=self.uk.id)  # обновление закэшированых разрешений
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.post(f'{endpoint_url}', {})
        self.assertEqual(response.status_code, 403)


class ContribInfoUpdateViewSetTest(BaseTest):
    def test_creates_object(self):
        notify = mixer.blend(Notify, organization=self.admin.organization)
        other_notify = mixer.blend(Notify, organization=self.uk.organization)
        contrib = mixer.blend(ContributionsInformation, notify=notify)
        m1 = mixer.blend(ContributionsInformationMistake)
        m2 = mixer.blend(ContributionsInformationMistake)
        file = mixer.blend(File, owner=mixer.SELECT)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        json_data = {
            "id": contrib.id,
            "notify": {"id": other_notify.id},
            "status": {"id": 1},
            "files": [{"id": file.id}],
            "mistakes": [{"id": m1.id}, {"id": m2.id}],
            "date": "2020-09-23",
            "assessed_contributions_total": "11",
            "assessed_contributions_current": "22",
            "received_contributions_total": "33",
            "received_contributions_current": "44",
            "delta_total": "55",
            "funds_spent": "12",
            "credit": "23",
            "funds_on_special_deposit": "34",
            "fund_balance": "66",
            "comment": "45",
            "comment2": "56"
        }
        response = client.patch(f'{endpoint_url}{contrib.id}/', json_data, format='json')
        contrib = ContributionsInformation.objects.get(id=contrib.id)
        self.assertEqual(response.data['id'], contrib.id)
        self.assertEqual(contrib.status.id, 1)
        self.assertEqual(contrib.notify, other_notify)
        self.assertEqual([m1, m2], list(contrib.mistakes.all()))
        self.assertEqual([file], list(contrib.files.all()))
        self.assertEqual(contrib.assessed_contributions_total, 11)
        self.assertEqual(contrib.assessed_contributions_current, 22)
        self.assertEqual(contrib.received_contributions_total, 33)
        self.assertEqual(contrib.received_contributions_current, 44)
        self.assertEqual(contrib.delta_total, 55)
        self.assertEqual(contrib.funds_spent, 12)
        self.assertEqual(contrib.credit, 23)
        self.assertEqual(contrib.funds_on_special_deposit, 34)
        self.assertEqual(contrib.fund_balance, 66)
        self.assertEqual(contrib.comment, '45')
        self.assertEqual(contrib.comment2, '56')

    def test_does_not_allow_uk_set_status_more_than_2(self):
        notify = mixer.blend(Notify, organization=self.uk.organization)
        contrib = mixer.blend(ContributionsInformation, notify=notify, status_id=1)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        json_data = {
            "id": 0,
            "notify": {"id": notify.id},
            "status": {"id": 3},
            "files": [],
            "mistakes": [],
        }
        response = client.patch(f'{endpoint_url}{contrib.id}/', json_data, format='json')
        contrib = ContributionsInformation.objects.get(id=contrib.id)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(contrib.status.id, 1)

    def test_does_not_allow_save_uk_some_fields(self):
        notify = mixer.blend(Notify, organization=self.uk.organization)
        date = datetime.date(2000, 12, 10)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        m1 = mixer.blend(ContributionsInformationMistake)
        m2 = mixer.blend(ContributionsInformationMistake)
        contrib = mixer.blend(ContributionsInformation, notify=notify, status_id=1, date=date, mistakes=[m1, m2])
        json_data = {
            "id": 0,
            "date": "2003-12-24",
            "notify": {"id": notify.id},
            "status": {"id": 1},
            "files": [],
            "mistakes": [{"id": m1.id}],
        }
        for field in ContributionsInformationViewSet.additional_fields:
            json_data[field] = field
        response = client.patch(f'{endpoint_url}{contrib.id}/', json_data, format='json')
        contrib = ContributionsInformation.objects.get(id=contrib.id)
        self.assertEqual(datetime.datetime.strptime(response.data['date'], '%Y-%m-%d').date(), date,
                         msg='Должна остаться старая дата')
        self.assertEqual(contrib.date, date, msg='Должна остаться старая дата')

        self.assertEqual(contrib.mistakes.count(), 2)
        for field in ContributionsInformationViewSet.additional_fields:
            self.assertTrue(field not in response.data, msg=f'{field} не должно выдаваться УК')
            self.assertEqual(contrib.__getattribute__(field), None, msg=f'{field} должно было остаться пустым')

    def test_uk_cant_set_not_its_own_notify(self):
        notify = mixer.blend(Notify, organization=self.uk.organization)
        contrib = mixer.blend(ContributionsInformation, notify=notify, status_id=1)
        other_notify = mixer.blend(Notify, organization=self.admin.organization)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        json_data = {
            "id": 0,
            "notify": {"id": other_notify.id},
            "status": {"id": 1},
            "files": [],
            "mistakes": [],
        }
        response = client.patch(f'{endpoint_url}{contrib.id}/', json_data, format='json')
        contrib = ContributionsInformation.objects.get(id=contrib.id)
        self.assertTrue(response.status_code, 400)
        self.assertTrue(contrib.notify, notify)

    def test_does_not_allow_uk_save_if_status_already_3(self):
        notify = mixer.blend(Notify, organization=self.uk.organization)
        contrib = mixer.blend(ContributionsInformation, notify=notify, status_id=3)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        json_data = {
            "id": 0,
            "delta_total": '123',
            "notify": {"id": notify.id},
            "status": {"id": 1},
            "files": [],
            "mistakes": [],
        }
        response = client.patch(f'{endpoint_url}{contrib.id}/', json_data, format='json')
        contrib = ContributionsInformation.objects.get(id=contrib.id)
        self.assertTrue(response.status_code, 400)
        self.assertEqual(contrib.delta_total, None)

    def test_setting_status_3_updates_latest_contrib_date_in_notify(self):
        notify = mixer.blend(Notify, organization=self.uk.organization)
        contrib = mixer.blend(ContributionsInformation, notify=notify, status_id=2)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        json_data = {
            "id": 0,
            "notify": {"id": notify.id},
            "status": {"id": 3},
            "files": [],
            "mistakes": [],
        }
        response = client.patch(f'{endpoint_url}{contrib.id}/', json_data, format='json')
        notify = Notify.objects.get(id=notify.id)
        self.assertEqual(notify.latest_contrib_date, datetime.datetime.now().date())

    def test_needs_authentification(self):
        client = APIClient()
        notify = mixer.blend(Notify, organization=self.uk.organization)
        contrib = mixer.blend(ContributionsInformation, notify=notify, status_id=2)
        response = client.patch(f'{endpoint_url}{contrib.id}/',{})
        self.assertEqual(response.status_code, 401)

    def test_needs_permission(self):
        self.uk.groups.set([])
        self.uk.save()
        self.uk = User.objects.get(id=self.uk.id)  # обновление закэшированых разрешений
        notify = mixer.blend(Notify, organization=self.uk.organization)
        contrib = mixer.blend(ContributionsInformation, notify=notify, status_id=2)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.patch(f'{endpoint_url}{contrib.id}/',{})
        self.assertEqual(response.status_code, 403)


class ContribInfoRetrieveViewSetTest(BaseTest):
    def test_returns_object(self):
        notify = mixer.blend(Notify, organization=self.uk.organization)
        contrib = mixer.blend(ContributionsInformation, notify=notify, status_id=2)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.get(f'{endpoint_url}{contrib.id}/', )
        self.assertEqual(response.data['id'], contrib.id)
        self.assertEqual(response.data['funds_spent'], contrib.funds_spent)

    def test_uk_can_see_its_own_notifies(self):
        """Управляющие организации не должны видеть уведомления других"""
        notify = mixer.blend(Notify, organization=self.admin.organization)
        contrib = mixer.blend(ContributionsInformation, notify=notify, status_id=2)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.get(f'{endpoint_url}{contrib.id}/')
        self.assertEqual(response.status_code, 404)

    def test_uk_cant_see_additional_fields(self):
        notify = mixer.blend(Notify, organization=self.uk.organization)
        contrib = mixer.blend(ContributionsInformation, notify=notify, status_id=2)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.get(f'{endpoint_url}{contrib.id}/')
        self.assertTrue('delta_total' in response.data)
        for field in ContributionsInformationViewSet.additional_fields:
            self.assertTrue(field not in response.data, msg=f'{field} не должно выдаваться УК')

        notify = mixer.blend(Notify)
        contrib = mixer.blend(ContributionsInformation, notify=notify, status_id=2)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.get(f'{endpoint_url}{contrib.id}/')
        self.assertTrue('delta_total' in response.data)
        for field in ContributionsInformationViewSet.additional_fields:
            self.assertTrue(field in response.data, msg=f'{field} должно выдаваться администратору')

    def test_needs_authentification(self):
        notify = mixer.blend(Notify)
        contrib = mixer.blend(ContributionsInformation, notify=notify, status_id=2)
        client = APIClient()
        response = client.get(f'{endpoint_url}{contrib.id}/')
        self.assertEqual(response.status_code, 401)

    def test_needs_permission(self):
        notify = mixer.blend(Notify)
        contrib = mixer.blend(ContributionsInformation, notify=notify, status_id=2)
        self.uk.groups.set([])
        self.uk.save()
        self.uk = User.objects.get(id=self.uk.id)  # обновление закэшированых разрешений
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.get(f'{endpoint_url}{contrib.id}/')
        self.assertEqual(response.status_code, 403)