from iggnpk.tests.base import BaseTest
from dictionaries.models import Organization, OrganizationType
from mixer.backend.django import mixer

from tools.service import upd_foreign_key, ServiceException


class UpdForeignKeyTest(BaseTest):
    def test_updates_field(self):
        """Функция должна обновить поле field если в data передан id нового объекта"""
        org_type = mixer.blend(OrganizationType)
        new_org_type = mixer.blend(OrganizationType)
        org = mixer.blend(Organization, type=org_type)
        data = {'type': {'id': new_org_type.id, 'text': 'some text'}}
        result = upd_foreign_key('type', data, org, OrganizationType)
        self.assertEqual(result, new_org_type)

    def test_pass_if_id_not_in_field_data_dict(self):
        """ Функция должна возратить текущее значения поля field объекта,
            если в словаре data не передан id нового значения"""
        org_type = mixer.blend(OrganizationType)
        org = mixer.blend(Organization, type=org_type)
        data = {'type': {'text': 'some text'}}
        result = upd_foreign_key('type', data, org, OrganizationType)
        self.assertEqual(result, org_type)

    def test_pass_if_field_not_in_data_dict(self):
        """Функция должна возвратить текущее значение поля field объекта,
            если в словаре data нет ключа с названием этого поля"""
        org_type = mixer.blend(OrganizationType)
        new_org_type = mixer.blend(OrganizationType)
        org = mixer.blend(Organization, type=org_type)
        data = {'some_other_field': {'id': new_org_type.id, 'text': 'some text'}}
        result = upd_foreign_key('type', data, org, OrganizationType)
        self.assertEqual(result, org_type)

    def test_raise_service_exception_if_instance_and_field_in_data_is_none(self):
        """Функция должна возбудить ошибку, если и instance равен None и в словаре data нет ключа field"""
        org_type = mixer.blend(OrganizationType)
        new_org_type = mixer.blend(OrganizationType)
        org = mixer.blend(Organization, type=org_type)
        data = {'some_other_field': {'id': new_org_type.id, 'text': 'some text'}}
        try:
            upd_foreign_key('type', data, None, OrganizationType)
            raise AssertionError
        except ServiceException:
            pass
