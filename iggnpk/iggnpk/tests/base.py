from django.test import TestCase
from rest_framework.test import APIRequestFactory

from iggnpk.tests import data


class BaseTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        data.create_organizations()
        data.create_conrib_infos()