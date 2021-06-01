from celery import shared_task
from django.core.mail import EmailMessage
from tools.import_from_excel import houses, regional_program


@shared_task
def import_houses_from_register_of_licenses():
    """Выгрузка информации о домах из реестра лицензий"""
    houses()


@shared_task
def import_houses_from_register_of_KR(path, email):
    """Выгрузка информации о домах из реестра капитального ремонта"""
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
