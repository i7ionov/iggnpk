from celery import shared_task
from django.core.mail import send_mail, EmailMessage

from tools.import_from_excel import houses, regional_program


@shared_task
def import_houses_from_register_of_licenses():
    houses()

@shared_task
def import_houses_from_register_of_KR(path, email):
    errors = regional_program(path)
    message = 'Импорт завершен. Перечень невыгруженных домов:\n '
    for err in errors:
        message += err+';\n'
    email = EmailMessage(
        f'Акты',
        message,
        'noreply@iggnpk.ru',
        [email],
        headers={'Reply-To': 'noreply@iggnpk.ru'}
    )
    email.send()
