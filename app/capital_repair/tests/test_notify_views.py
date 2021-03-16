import time

from django.test import override_settings

from capital_repair.models import Notify, CreditOrganization
from capital_repair.views import NotifiesViewSet
from dictionaries.models import User, Organization, House, Address, File
from iggnpk.tests.base import BaseTest

from rest_framework.test import APIClient
from mixer.backend.django import mixer

endpoint_url = '/api/v1/cr/notifies/'

class NotifiesListViewSetTest(BaseTest):
    def test_returns_dict(self):
        id = Notify.objects.first().id
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.get(f'{endpoint_url}?filter=["id","=",{id}]')
        self.assertTrue('items' in response.data)
        self.assertTrue('totalCount' in response.data)
        self.assertTrue('summary' in response.data)

    def test_uk_can_see_its_own_notifies(self):
        """Управляющие организации не должны видеть уведомления других"""
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.get(f'{endpoint_url}')
        self.assertEqual(response.data['totalCount'], Notify.objects.filter(organization=self.uk.organization).count())
        for n in response.data['items']:
            self.assertEqual(n['organization']['id'], self.uk.organization.id,
                             msg=f"Уведомление с id {n['id']} принадлежит организации {n['organization']['id']}, хотя должно {self.uk.organization.id}")
        # в том числе через фильтрацию
        other_org = mixer.blend(Organization)
        other_notify = mixer.blend(Notify, organization=other_org)
        response = client.get(f'{endpoint_url}?filter=["id","=",{other_notify.id}]')
        self.assertEqual(response.data['totalCount'], 0,
                         msg='УК не должна видеть не свои уведомления даже после фильтрации')
        self.assertEqual(len(response.data['items']), 0,
                         msg='УК не должна видеть не свои уведомления даже после фильтрации')
        # администратор должен видеть все
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.get(f'{endpoint_url}?filter=["id","=",{other_notify.id}]')
        self.assertEqual(response.data['totalCount'], 1,
                         msg='Администратор должнен видеть все уведомления')
        self.assertEqual(len(response.data['items']), 1,
                         msg='Администратор должнен видеть все уведомления')
        response = client.get(f'{endpoint_url}')
        self.assertEqual(response.data['totalCount'], Notify.objects.all().count())

    def test_uk_cant_see_additional_fields(self):
        """Управляющие организации не должны видеть дополнительные поля"""
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.get(f'{endpoint_url}')
        for field in NotifiesViewSet.additional_fields:
            self.assertTrue(field in response.data['items'][0], msg=f'{field} должно выдаваться администратору')
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        mixer.blend(Notify, organization=self.uk.organization)
        response = client.get(f'{endpoint_url}')
        for field in NotifiesViewSet.additional_fields:
            self.assertTrue(field not in response.data['items'][0], msg=f'{field} не должно выдаваться УК')

    def test_filter_group_dates(self):
        # сгруппированные значения долджны передаваться в поле key объектов массива items
        """
        {'totalCount': 5,
        'items': [
        {'key': None, 'items': []},
        {'key': 2012, 'items': [
                                {'key': 11, 'items': [{'key': 15, 'items': None}]},
                                {'key': 12, 'items': [{'key': 14, 'items': None},
                                                      {'key': 15, 'items': None}]}]},
        {'key': 2013, 'items': [{'key': 11, 'items': [{'key': 15, 'items': None}]}]}]}
        """
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        mixer.blend(Notify, date=datetime.date(2012, 12, 14))
        mixer.blend(Notify, date=datetime.date(2012, 12, 15))
        mixer.blend(Notify, date=datetime.date(2012, 11, 15))
        mixer.blend(Notify, date=datetime.date(2013, 11, 15))
        response = client.get(
            endpoint_url+'?group=[{%22selector%22:%22date%22,%22groupInterval%22:%22year%22,%22isExpanded%22:true},{%22selector%22:%22date%22,%22groupInterval%22:%22month%22,%22isExpanded%22:true},{%22selector%22:%22date%22,%22groupInterval%22:%22day%22,%22isExpanded%22:false}]')
        self.assertTrue('items' in response.data)
        self.assertTrue('totalCount' in response.data)
        self.assertTrue('key' in response.data['items'][0])
        self.assertEqual(response.data['items'][1]['key'], 2012)
        self.assertEqual(response.data['items'][2]['key'], 2013)
        self.assertEqual(response.data['items'][1]['items'][0]['key'], 11)
        self.assertEqual(response.data['items'][1]['items'][0]['items'][0]['key'], 15)
        self.assertEqual(response.data['items'][1]['items'][1]['key'], 12)
        self.assertEqual(response.data['items'][1]['items'][1]['items'][0]['key'], 14)
        self.assertEqual(response.data['items'][1]['items'][1]['items'][1]['key'], 15)

    def test_allow_search_by_defined_fields(self):
        """Должен производиться поиск по следующим полям: id, номер счета, поля адреса"""
        house = mixer.blend(House, address=mixer.blend(Address, area='area', city='city', street='street'),
                            number='number')
        notify = mixer.blend(Notify, organization=self.uk.organization, status_id=3, house=house,
                             account_number='account_number')
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.get(f'{endpoint_url}?searchValue=%22account_number%22&searchExpr=undefined')
        self.assertEqual(response.data['items'][0]['id'], notify.id)
        response = client.get(f'/api/v1/cr/notifies/?searchValue=%22area%22&searchExpr=undefined')
        self.assertEqual(response.data['items'][0]['id'], notify.id)
        response = client.get(f'/api/v1/cr/notifies/?searchValue=%22city%22&searchExpr=undefined')
        self.assertEqual(response.data['items'][0]['id'], notify.id)
        response = client.get(f'/api/v1/cr/notifies/?searchValue=%22street%22&searchExpr=undefined')
        self.assertEqual(response.data['items'][0]['id'], notify.id)
        response = client.get(f'/api/v1/cr/notifies/?searchValue=%22number%22&searchExpr=undefined')
        self.assertEqual(response.data['items'][0]['id'], notify.id)

    def test_pagination(self):
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.get(f'{endpoint_url}?skip=0&take=20')
        self.assertEqual(len(response.data['items']), 20)

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


class NotifiesCreateViewSetTest(BaseTest):
    def test_creates_object(self):
        bank = mixer.blend(CreditOrganization)
        address = mixer.blend(Address)
        file = mixer.blend(File, owner=mixer.SELECT)
        mixer.blend(File, owner=mixer.SELECT)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.post(f'{endpoint_url}', {
            "id": 0,
            "house": {
                "id": 0,
                "address": {
                    "id": address.id,
                    "area": "qwer",
                    "place": "qwer",
                    "city": "qwer",
                    "city_weight": 50,
                    "street": "rewd"
                },
                "organization": {
                    "id": 0
                },
                "number": "3"
            },
            "organization": {
                "id": self.admin.organization.id,
                "type": {
                    "id": 1,
                    "text": "ТСЖ"
                },
                "inn": "qwe",
                "ogrn": "qwe",
                "name": "qwe"
            },
            "bank": {
                "id": bank.id,
                "name": "qwe",
                "inn": "qwe",
                "allow_to_select": 'false'
            },
            "files": [{
                "id": file.id,
                "owner": 1,
                "datafile": "/media/123/1.pdf",
                "size": 206767,
                "created": "2020-12-24T14:26:05.402134+05:00",
                "name": "file.pdf"
            }],
            "status": {
                "id": 2
            },
            "date": "2020-12-24",
            "account_number": "111",
            "account_opening_date": "2020-12-17",
            "monthly_contribution_amount": 333,
            "protocol_details": "444",
            "comment": "555",
            "comment2": "666",
            "date_of_exclusion": "2020-12-09",
            "account_closing_date": "2020-12-10",
            "ground_for_exclusion": "453",
            "source_of_information": "3333"
        }, format='json')
        notify = Notify.objects.last()
        self.assertEqual(response.data['id'], notify.id)
        self.assertEqual(notify.house.address_id, address.id)
        self.assertEqual(notify.house_id, House.objects.last().id)
        self.assertEqual(notify.house.number, '3')
        self.assertEqual(notify.organization.id, self.admin.organization.id)
        self.assertEqual(notify.bank.id, bank.id)
        self.assertEqual(notify.status.id, 2)
        self.assertEqual(len(notify.files.all()), 1)
        self.assertEqual(notify.date, datetime.date.today())
        self.assertEqual(notify.account_number, '111')
        self.assertEqual(notify.account_opening_date, datetime.date(2020, 12, 17))
        self.assertEqual(notify.monthly_contribution_amount, 333)
        self.assertEqual(notify.protocol_details, '444')
        self.assertEqual(notify.comment, '555')
        self.assertEqual(notify.comment2, '666')
        self.assertEqual(notify.date_of_exclusion, datetime.date(2020, 12, 9))
        self.assertEqual(notify.account_closing_date, datetime.date(2020, 12, 10))
        self.assertEqual(notify.ground_for_exclusion, '453')
        self.assertEqual(notify.source_of_information, '3333')

    def test_does_not_allow_status_more_than_2(self):
        previous_notify = mixer.blend(Notify)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        bank = mixer.blend(CreditOrganization)
        address = mixer.blend(Address)
        mixer.blend(File, owner=mixer.SELECT)
        response = client.post(f'{endpoint_url}', {
            "id": 0,
            "monthly_contribution_amount": 333,
            "protocol_details": "444",
            "bank": {
                "id": bank.id,
            },
            "organization": {
                "id": self.admin.organization.id,
            },
            "house": {
                "id": 1,
                "number": '3',
                "address": {
                    "id": address.id,
                },
            },
            "status": {
                "id": 3
            },

        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue(previous_notify, Notify.objects.last())

    def test_creates_house_only_its_doesnt_exists(self):
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        bank = mixer.blend(CreditOrganization)
        house = mixer.blend(House, number='23')
        response = client.post(f'{endpoint_url}', {
            "id": 0,
            "monthly_contribution_amount": 333,
            "protocol_details": "444",
            "bank": {
                "id": bank.id,
            },
            "organization": {
                "id": self.admin.organization.id,
            },
            "house": {
                "id": house.id,
                "number": house.number,
                "address": {
                    "id": house.address.id,
                },
            },
            "status": {
                "id": 1
            },

        }, format='json')
        self.assertEqual(response.data['house']['id'], house.id)

    def test_does_not_allow_save_uk_some_fields(self):
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        bank = mixer.blend(CreditOrganization)
        organization = mixer.blend(Organization)
        house = mixer.blend(House, number='23')
        json_data = {
            "id": 0,
            "date": "2000-12-24",
            "monthly_contribution_amount": 333,
            "protocol_details": "444",
            "bank": {
                "id": bank.id,
            },
            "organization": {
                "id": organization.id,
            },
            "house": {
                "id": house.id,
                "number": house.number,
                "address": {
                    "id": house.address.id,
                },
            },
            "status": {
                "id": 1
            },

        }
        for field in NotifiesViewSet.additional_fields:
            json_data[field] = field
        response = client.post(f'{endpoint_url}', json_data, format='json')
        notify = Notify.objects.get(id=response.data['id'] )
        self.assertEqual(response.data['organization']['id'], self.uk.organization.id,
                         msg='Должна записаться организация пользователя')
        self.assertEqual(datetime.datetime.strptime(response.data['date'],'%Y-%m-%d').date(), datetime.date.today(),
                         msg='Должна записаться текущая дата')

        for field in NotifiesViewSet.additional_fields:
            self.assertTrue(field not in response.data, msg=f'{field} не должно выдаваться УК')
            self.assertEqual(notify.__getattribute__(field),None, msg=f'{field} должно было остаться пустым')

    def test_needs_authentification(self):
        client = APIClient()
        response = client.post(f'{endpoint_url}',{})
        self.assertEqual(response.status_code, 401)

    def test_needs_permission(self):
        self.uk.groups.set([])
        self.uk.save()
        self.uk = User.objects.get(id=self.uk.id)  # обновление закэшированых разрешений
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.post(f'/api/v1/cr/notifies/', {})
        self.assertEqual(response.status_code, 403)


class NotifiesRetrieveViewSetTest(BaseTest):
    def test_returns_object(self):
        notify = mixer.blend(Notify, organization=self.uk.organization)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.get(f'{endpoint_url}{notify.id}/',)
        self.assertEqual(response.data['id'] ,notify.id)
        self.assertEqual(response.data['monthly_contribution_amount'], notify.monthly_contribution_amount)

    def test_uk_can_see_its_own_notifies(self):
        """Управляющие организации не должны видеть уведомления других"""
        notify = mixer.blend(Notify, organization=self.admin.organization)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.get(f'{endpoint_url}{notify.id}/')
        self.assertEqual(response.status_code, 404)

    def test_uk_cant_see_additional_fields(self):
        notify = mixer.blend(Notify, organization=self.uk.organization)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.get(f'{endpoint_url}{notify.id}/')
        self.assertTrue('protocol_details' in response.data)
        for field in NotifiesViewSet.additional_fields:
            self.assertTrue(field not in response.data, msg=f'{field} не должно выдаваться УК')

        notify = mixer.blend(Notify)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.get(f'{endpoint_url}{notify.id}/')
        self.assertTrue('protocol_details' in response.data)
        for field in NotifiesViewSet.additional_fields:
            self.assertTrue(field in response.data, msg=f'{field} должно выдаваться администратору')

    def test_needs_authentification(self):
        notify = mixer.blend(Notify)
        client = APIClient()
        response = client.get(f'{endpoint_url}{notify.id}/')
        self.assertEqual(response.status_code, 401)

    def test_needs_permission(self):
        notify = mixer.blend(Notify)
        self.uk.groups.set([])
        self.uk.save()
        self.uk = User.objects.get(id=self.uk.id)  # обновление закэшированых разрешений
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.get(f'{endpoint_url}{notify.id}/')
        self.assertEqual(response.status_code, 403)


class NotifiesUpdateViewSetTest(BaseTest):
    def test_updates_object(self):
        notify = mixer.blend(Notify)
        bank = mixer.blend(CreditOrganization)
        address = mixer.blend(Address)
        file1 = mixer.blend(File, owner=mixer.SELECT)
        file2 = mixer.blend(File, owner=mixer.SELECT)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.patch(f'{endpoint_url}{notify.id}/', {
            "id": notify.id,
            "house": {
                "id": 0,
                "address": {
                    "id": address.id,
                    "area": "qwer",
                    "place": "qwer",
                    "city": "qwer",
                    "city_weight": 50,
                    "street": "rewd"
                },
                "organization": {
                    "id": 0
                },
                "number": "3"
            },
            "organization": {
                "id": self.admin.organization.id,
                "type": {
                    "id": 1,
                    "text": "ТСЖ"
                },
                "inn": "qwe",
                "ogrn": "qwe",
                "name": "qwe"
            },
            "bank": {
                "id": bank.id,
                "name": "qwe",
                "inn": "qwe",
                "allow_to_select": 'false'
            },
            "files": [{
                "id": file1.id,
                "owner": 1,
                "datafile": "/media/123/1.pdf",
                "size": 206767,
                "created": "2020-12-24T14:26:05.402134+05:00",
                "name": "file.pdf"
            }],
            "status": {
                "id": 3
            },
            "date": "2020-12-24",
            "account_number": "111",
            "account_opening_date": "2020-12-17",
            "monthly_contribution_amount": 333,
            "protocol_details": "444",
            "comment": "555",
            "comment2": "666",
            "date_of_exclusion": "2020-12-09",
            "account_closing_date": "2020-12-10",
            "ground_for_exclusion": "453",
            "source_of_information": "3333"
        }, format='json')
        notify = Notify.objects.get(id=notify.id)
        self.assertEqual(response.data['id'], notify.id)
        self.assertEqual(notify.house.address_id, address.id)
        self.assertEqual(notify.house_id, House.objects.last().id)
        self.assertEqual(notify.house.number, '3')
        self.assertEqual(notify.organization.id, self.admin.organization.id)
        self.assertEqual(notify.bank.id, bank.id)
        self.assertEqual(notify.status.id, 3)
        self.assertEqual(len(notify.files.all()), 1)
        self.assertEqual(notify.date, datetime.date(2020, 12, 24))
        self.assertEqual(notify.account_number, '111')
        self.assertEqual(notify.account_opening_date, datetime.date(2020, 12, 17))
        self.assertEqual(notify.monthly_contribution_amount, 333)
        self.assertEqual(notify.protocol_details, '444')
        self.assertEqual(notify.comment, '555')
        self.assertEqual(notify.comment2, '666')
        self.assertEqual(notify.date_of_exclusion, datetime.date(2020, 12, 9))
        self.assertEqual(notify.account_closing_date, datetime.date(2020, 12, 10))
        self.assertEqual(notify.ground_for_exclusion, '453')
        self.assertEqual(notify.source_of_information, '3333')

    def test_does_not_allow_uk_set_status_more_than_2(self):
        notify = mixer.blend(Notify, organization = self.uk.organization, status_id=1)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        bank = mixer.blend(CreditOrganization)
        address = mixer.blend(Address)
        mixer.blend(File, owner=mixer.SELECT)
        response = client.patch(f'{endpoint_url}{notify.id}/', {
            "id": notify.id,
            "monthly_contribution_amount": 333,
            "protocol_details": "444",
            "bank": {
                "id": bank.id,
            },
            "organization": {
                "id": self.admin.organization.id,
            },
            "house": {
                "id": 1,
                "number": '3',
                "address": {
                    "id": address.id,
                },
            },
            "status": {
                "id": 3
            },

        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_creates_house_only_its_doesnt_exists(self):
        notify = mixer.blend(Notify)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        bank = mixer.blend(CreditOrganization)
        house = mixer.blend(House, number='23')
        response = client.patch(f'{endpoint_url}{notify.id}/', {
            "id": notify.id,
            "monthly_contribution_amount": 333,
            "protocol_details": "444",
            "bank": {
                "id": bank.id,
            },
            "organization": {
                "id": self.admin.organization.id,
            },
            "house": {
                "id": house.id,
                "number": house.number,
                "address": {
                    "id": house.address.id,
                },
            },
            "status": {
                "id": 1
            },

        }, format='json')
        self.assertEqual(response.data['house']['id'], house.id)

    def test_does_not_allow_save_uk_some_fields(self):
        date = datetime.date(2000, 12, 10)
        notify = mixer.blend(Notify, organization=self.uk.organization, status_id=1, date=date)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        bank = mixer.blend(CreditOrganization)
        organization = mixer.blend(Organization)
        house = mixer.blend(House, number='23')
        json_data = {
            "id": notify.id,
            "date": "2003-12-24",
            "monthly_contribution_amount": 333,
            "protocol_details": "444",
            "bank": {
                "id": bank.id,
            },
            "organization": {
                "id": organization.id,
            },
            "house": {
                "id": house.id,
                "number": house.number,
                "address": {
                    "id": house.address.id,
                },
            },
            "status": {
                "id": 1
            },

        }
        for field in NotifiesViewSet.additional_fields:
            json_data[field] = field
        response = client.patch(f'{endpoint_url}{notify.id}/', json_data, format='json')
        notify = Notify.objects.get(id=notify.id)
        self.assertEqual(response.data['organization']['id'], self.uk.organization.id,
                         msg='Должна остаться организация пользователя')
        self.assertEqual(datetime.datetime.strptime(response.data['date'],'%Y-%m-%d').date(), date,
                         msg='Должна остаться предыдущая дата')
        self.assertEqual(notify.organization.id, self.uk.organization.id,
                         msg='Должна остаться организация пользователя')
        self.assertEqual(notify.date, date,
                         msg='Должна остаться предыдущая дата')
        for field in NotifiesViewSet.additional_fields:
            self.assertTrue(field not in response.data, msg=f'{field} не должно выдаваться УК')
            self.assertEqual(notify.__getattribute__(field),None, msg=f'{field} должно было остаться пустым')

    def test_does_not_allow_uk_save_if_status_already_3(self):
        notify = mixer.blend(Notify, organization=self.uk.organization, status_id=3)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        bank = mixer.blend(CreditOrganization)
        organization = mixer.blend(Organization)
        house = mixer.blend(House, number='23')
        response = client.patch(f'{endpoint_url}{notify.id}/', {
            "id": notify.id,
            "date": "2003-12-24",
            "monthly_contribution_amount": 333,
            "protocol_details": "444",
            "bank": {
                "id": bank.id,
            },
            "organization": {
                "id": organization.id,
            },
            "house": {
                "id": house.id,
                "number": house.number,
                "address": {
                    "id": house.address.id,
                },
            },
            "status": {
                "id": 1
            },

        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_needs_authentification(self):
        client = APIClient()
        response = client.patch(f'{endpoint_url}1/',{})
        self.assertEqual(response.status_code, 401)

    def test_needs_permission(self):
        self.uk.groups.set([])
        self.uk.save()
        self.uk = User.objects.get(id=self.uk.id)  # обновление закэшированых разрешений
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.patch(f'{endpoint_url}1/', {})
        self.assertEqual(response.status_code, 403)


class NotifiesGenerateActsViewSetTest(BaseTest):
    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       CELERY_ALWAYS_EAGER=True,
                       BROKER_BACKEND='memory')
    def test_response_200_object(self):
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.get(f'{endpoint_url}generate_acts/', {})
        self.assertEqual(response.status_code, 200)

    def test_does_not_allow_uk(self):
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.get(f'{endpoint_url}generate_acts/', {})
        self.assertEqual(response.status_code, 400)

    def test_needs_authentification(self):
        client = APIClient()
        response = client.get(f'{endpoint_url}generate_acts/',{})
        self.assertEqual(response.status_code, 401)

    def test_needs_permission(self):
        self.uk.groups.set([])
        self.uk.save()
        self.uk = User.objects.get(id=self.uk.id)  # обновление закэшированых разрешений
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.uk_token.key)
        response = client.get(f'{endpoint_url}generate_acts/', {})
        self.assertEqual(response.status_code, 403)

class NotifiesGetHistoryViewSetTest(BaseTest):
    def test_response_200_object(self):
        notify = mixer.blend(Notify, organization=self.uk.organization)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.get(f'{endpoint_url}{notify.id}/get_history/', {})
        self.assertEqual(response.status_code, 200)

    def test_returns_list(self):
        notify = mixer.blend(Notify, organization=self.uk.organization)
        # между записями в базе должно пройти как минимум секунда, чтобы история корректно сохранилась
        time.sleep(1)
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.patch(f'{endpoint_url}{notify.id}/', {
            "id": notify.id,
            "comment": "test comment",
        }, format='json')
        time.sleep(1)
        bank = mixer.blend(CreditOrganization)
        notify.bank = bank
        notify.save()
        client = APIClient(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = client.get(f'{endpoint_url}{notify.id}/get_history/', {})

        self.assertEqual(response.data[0]['delta'][0]['field'], 'bank')
        self.assertEqual(response.data[0]['delta'][0]['field_verbose'], 'Кредитная организация')
        self.assertEqual(response.data[0]['delta'][0]['new'], bank.id)
        self.assertEqual(response.data[0]['delta'][0]['old'], None)
        self.assertEqual(response.data[0]['history_type'], '~')

        self.assertEqual(response.data[1]['delta'][0]['field'], 'comment')
        self.assertEqual(response.data[1]['delta'][0]['field_verbose'], 'Комментарий')
        self.assertEqual(response.data[1]['delta'][0]['new'], 'test comment')
        self.assertEqual(response.data[1]['delta'][0]['old'], None)
        self.assertEqual(response.data[1]['history_user'], 'admin')

        self.assertEqual(len(response.data[2]['delta']), 0)
        self.assertEqual(response.data[2]['history_type'], '+')

