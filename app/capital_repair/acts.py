from io import BytesIO
from datetime import date
from dateutil.relativedelta import relativedelta
from django.core.files.base import ContentFile
from capital_repair.models import Notify, ContributionsInformationMistake
from dictionaries.models import Organization, File, User
from tools import dev_extreme, date_tools
from iggnpk import settings
from docxtpl import DocxTemplate
import io
import os
import zipfile


class Act:
    @staticmethod
    def report_month():
        """ Возвращает месяц, до начала которого должны были подать отчет о взносах: январь, апрель, июль или октябрь """
        if date.today() < date(date.today().year, 3, 20):
            month = 1
        elif date.today() < date(date.today().year, 6, 20):
            month = 4
        elif date.today() < date(date.today().year, 9, 20):
            month = 7
        else:
            month = 10
        return month

    @staticmethod
    def is_not_in_reporting_period(d):
        """ Определяет, относится ли эта дата к отчетному периоду. True - не относится """
        month = Act.report_month()
        return d < (date(date.today().year, month, 1) + relativedelta(months=-1))

    @staticmethod
    def reporting_quarter_date():
        """ Возвращает дату начала отчетного периода """
        month = Act.report_month()
        return date(date.today().year, month, 20) + relativedelta(months=-1)

    @staticmethod
    def last_reporting_date():
        """ Возвращает дату окончания отчетного периода """
        month = Act.report_month()
        return date(date.today().year, month, 1)

    @staticmethod
    def generate_act_contexts(request_GET):
        """ Создает массив данных (контекстов) для последующей подстановки в темплейты актов """
        contexts = []
        queryset = Notify.objects.all()
        queryset, total_queryset, total_count = dev_extreme.filtered_query(request_GET, queryset)

        for org_id in total_queryset.order_by('organization').distinct('organization').values('organization__id'):
            org = Organization.objects.get(id=org_id['organization__id'])
            notifies = []
            mistakes = []
            paragraph = ''
            for notify in total_queryset.filter(organization=org):
                if notify.house is None or notify.organization is None:
                    continue
                contrib_info = notify.contributionsinformation_set.last()
                if contrib_info is None or Act.is_not_in_reporting_period(contrib_info.date):
                    # добавляем запись ошибки о том, что отчет не был подан
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
            mistakes_text = ', '.join(mistakes) + '.'
            mistakes_text = mistakes_text.replace('{reporting_quarter_date}',
                                                  date_tools.russian_date(Act.reporting_quarter_date()))
            mistakes_text = mistakes_text.replace('{last_reporting_date}',
                                                  date_tools.russian_date(Act.last_reporting_date()))
            contexts.append({'date': date_tools.russian_date(date.today()),
                       'organization': org,
                       'reporting_quarter_date': date_tools.russian_date(Act.reporting_quarter_date()),
                       'year': date.today().year,
                       'notifies': notifies,
                       'paragraph': paragraph,
                       'mistakes_text': mistakes_text})
        return contexts

    @staticmethod
    def add_file_into_db(bytes_file, mail):
        """ Добавляет сгенерированый файл в базу данных """
        user = User.objects.get(email=mail)
        content_file = ContentFile(bytes_file.getbuffer())
        file = File(owner=user, name='acts.zip')
        file.datafile.save('acts.zip', content_file, save=True)
        return file.uuid

    @staticmethod
    def zip_acts(request_GET, mail):
        """ Генерирует акты, пакует в zip архив и возвращает uuid файла для скачивания """
        bytes_file = BytesIO()
        with zipfile.ZipFile(bytes_file, "w") as zip_file:
            contexts = Act.generate_act_contexts(request_GET)
            for context in contexts:
                doc = DocxTemplate(os.path.join(settings.MEDIA_ROOT, 'templates', 'act_backend.docx'))
                doc.render(context)
                f = io.BytesIO()
                doc.save(f)
                org = context['organization']
                zip_file.writestr(org.name.replace('/', '') + ', ' + org.inn + '.docx', f.getvalue())
        uuid = Act.add_file_into_db(bytes_file, mail)
        return uuid
