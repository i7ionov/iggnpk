from celery import shared_task
from django.core.mail import send_mail

@shared_task
def hello():
    send_mail(
        f'Тест',
        f'Тест успешен',
        'noreply@iggnpk.ru',
        ['i7ionov@gmail.com'],
        fail_silently=False,
    )
    return 'Hello there!'
