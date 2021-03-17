from celery import shared_task
from django.core.mail import send_mail

from tools.import_from_excel import houses


@shared_task
def import_houses_from_register_of_licenses():
    houses()
