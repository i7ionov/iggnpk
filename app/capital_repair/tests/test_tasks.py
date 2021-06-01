from unittest.mock import patch, sentinel

from capital_repair.tasks import send_acts
from iggnpk.tests.base import BaseTest
from django.core import mail


class SendActsTest(BaseTest):
    @patch('capital_repair.acts.Act.zip_acts')
    def test_send_email(self, zip_acts):
        send_acts([],'test@email.ru')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(zip_acts.call_count, 1)
        m = mail.outbox[0]
        self.assertTrue('test@email.ru' in mail.outbox[0].to)
        self.assertIn('Ссылка на скачивание файла https://iggnpk.ru/', mail.outbox[0].body)