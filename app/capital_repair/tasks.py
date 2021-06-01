from celery import shared_task
from django.apps import apps
from django.core.mail import EmailMessage
from capital_repair.acts import Act
from tools import export_to_excel


@shared_task
def generate_excel(template_path, ids, model, mail):
    """ Экспортирует записи модели в формате xlsx и отправляет на указанный email.
        :param template_path путь к шаблону excel
        :param ids id записей для экспорта"""
    model = apps.get_model(model.split('.')[0], model.split('.')[1])
    queryset = model.objects.filter(id__in=ids)
    export_to_excel.export_to_excel(template_path,
                                    queryset,
                                    mail)


@shared_task
def send_acts(request_GET, mail):
    """ Отправляет акты о нарушениях по отфильтрованным уведомлениям на указанный email.
        Параметры для фильтрации передаются в request_GET в формате dev_extreme.filtered_query"""
    file_id = Act.zip_acts(request_GET, mail)
    email = EmailMessage(
        f'Акты',
        f'Ссылка на скачивание файла https://iggnpk.ru/api/v1/dict/files/{file_id}/',
        'noreply@iggnpk.ru',
        [mail],
        headers={'Reply-To': 'noreply@iggnpk.ru'}
    )
    email.send()
    return 'Success'
