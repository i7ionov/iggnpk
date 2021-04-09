from django.contrib.auth import authenticate
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.authtoken.models import Token

from iggnpk import settings
from iggnpk.tests import data


class BaseTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        data.populate_db()
        self.admin = authenticate(username='admin', password='123')
        self.admin_token, created = Token.objects.get_or_create(user=self.admin)
        self.uk = authenticate(username='uk', password='123')
        self.uk_token, created = Token.objects.get_or_create(user=self.uk)
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
