import io
import os
import zipfile
from datetime import datetime
from dateutil.relativedelta import relativedelta

from celery import shared_task
from django.apps import apps
from django.core.mail import EmailMessage
from docxtpl import DocxTemplate

from capital_repair.acts import Act
from capital_repair.models import Notify, ContributionsInformationMistake
from dictionaries.models import Organization
from iggnpk import settings
from tools import dev_extreme, date_tools, export_to_excel


@shared_task
def generate_excel(request_GET, template_path, ids, model, mail):
    model = apps.get_model(model.split('.')[0], model.split('.')[1])
    queryset = model.objects.filter(id__in=ids)
    #queryset, total_queryset, totalCount = dev_extreme.filtered_query(request_GET, model.objects.all())
    export_to_excel.export_to_excel(template_path,
                          queryset,
                          mail)
@shared_task
def send_acts(request_GET, mail):
    Act.zip_acts(request_GET, mail)
    email = EmailMessage(
        f'Акты',
        f'Ссылка на скачивание файла https://iggnpk.ru/media/temp/export_{mail}.zip',
        'noreply@iggnpk.ru',
        [mail],
        headers={'Reply-To': 'noreply@iggnpk.ru'}
    )
    email.send()
    return 'Success'
