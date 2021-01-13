import io
import os
import zipfile
from datetime import datetime


from celery import shared_task
from django.core.mail import EmailMessage
from docxtpl import DocxTemplate

from capital_repair.models import Notify, ContributionsInformationMistake
from dictionaries.models import Organization
from iggnpk import settings
from tools import dev_extreme, date


@shared_task
def send_acts(request_GET, mail):
    queryset = Notify.objects.all()
    response = io.BytesIO()
    zip_file = zipfile.ZipFile(response, "w")
    queryset, total_queryset, total_count = dev_extreme.filtered_query(request_GET, queryset)

    if datetime.now() < datetime(datetime.now().year, 3, 20):
        month = 12
    elif datetime.now() < datetime(datetime.now().year, 6, 20):
        month = 3
    elif datetime.now() < datetime(datetime.now().year, 9, 20):
        month = 6
    else:
        month = 9

    for org_id in total_queryset.order_by('organization').distinct('organization').values('organization__id'):

        org = Organization.objects.get(id=org_id['organization__id'])
        notifies = []
        mistakes = []
        mistakes_text = ''
        paragraph = ''
        for notify in total_queryset.filter(organization=org):
            if notify.house is None or notify.organization is None:
                continue
            contrib_info = notify.contributionsinformation_set.last()
            if contrib_info is None or contrib_info.date < datetime(datetime.now().year, month, 1).date():
                mistakes.append(ContributionsInformationMistake.objects.get(id=3).full_text)
                notifies.append(notify)
            else:
                for mistake in contrib_info.mistakes.all():
                    if mistake.id == 1:
                        paragraph = ' Пункта 6'
                    mistakes.append(mistake.full_text)
                if contrib_info.mistakes.count() > 0:
                    notifies.append(notify)
        mistakes = set(mistakes)
        if len(mistakes) == 0:
            continue
        for mistake in mistakes:
            mistakes_text = mistakes_text + mistake + ', '
        mistakes_text = mistakes_text[0:-2] + '.'
        mistakes_text = mistakes_text.replace('{reporting_quarter_date}',
                                              date.russian_date(datetime(datetime.now().year, month, 20)))
        mistakes_text = mistakes_text.replace('{last_reporting_date}',
                                              date.russian_date(datetime(datetime.now().year, month + 1, 1)))
        doc = DocxTemplate(os.path.join(settings.MEDIA_ROOT, 'templates', 'act_backend.docx'))
        context = {'date': date.russian_date(datetime.now()),
                   'organization': org,
                   'reporting_quarter_date': date.russian_date(datetime(datetime.now().year, month, 20)),
                   'year': datetime.now().year,
                   'notifies': notifies,
                   'paragraph': paragraph,
                   'mistakes_text': mistakes_text}
        doc.render(context)
        f = io.BytesIO()
        doc.save(f)
        zip_file.writestr(org.name.replace('/', '') + ', ' + org.inn + '.docx', f.getvalue())
    zip_file.close()
    email = EmailMessage(
        f'Акты',
        '',
        'noreply@iggnpk.ru',
        [mail],
        headers={'Reply-To': 'noreply@iggnpk.ru'}
    )
    email.attach('archive.zip', response.getvalue(), 'application/zip')
    email.send()

    return 'Hello there!'
