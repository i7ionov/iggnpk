from datetime import datetime
from dateutil.relativedelta import relativedelta
from capital_repair.models import Notify, ContributionsInformationMistake, ContributionsInformation
from dictionaries.models import Organization
from tools import dev_extreme, date
from iggnpk import settings
from docxtpl import DocxTemplate
import io
import os
import zipfile

class Act:
    @staticmethod
    def report_month():
        """Возвращает месяц, до начала которого должны были подать отчет о взносах: январь, апрель, июль или октябрь"""
        if datetime.now() < datetime(datetime.now().year, 3, 20):
            month = 1
        elif datetime.now() < datetime(datetime.now().year, 6, 20):
            month = 4
        elif datetime.now() < datetime(datetime.now().year, 9, 20):
            month = 7
        else:
            month = 10
        return month

    @staticmethod
    def is_not_in_reporting_period(date):
        """Определяет, относится ли эта дата к отчетному периоду. True - не относится"""
        month = Act.report_month()
        return date < (datetime(datetime.now().year, month, 1) + relativedelta(months=-1))

    @staticmethod
    def reporting_quarter_date():
        """Возвращает дату начала отчетного периода"""
        month = Act.report_month()
        return datetime(datetime.now().year, month, 20) + relativedelta(months=-1)

    @staticmethod
    def last_reporting_date():
        """Возвращает дату окончания отчетного периода"""
        month = Act.report_month()
        return datetime(datetime.now().year, month, 1)

    @staticmethod
    def generate_acts_by_notifies(request_GET):
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
                                                      date.russian_date(Act.reporting_quarter_date()))
            mistakes_text = mistakes_text.replace('{last_reporting_date}',
                                                      date.russian_date(Act.last_reporting_date()))
            contexts.append({'date': date.russian_date(datetime.now()),
                       'organization': org,
                       'reporting_quarter_date': date.russian_date(Act.reporting_quarter_date()),
                       'year': datetime.now().year,
                       'notifies': notifies,
                       'paragraph': paragraph,
                       'mistakes_text': mistakes_text})
        return contexts


    @staticmethod
    def zip_acts(request_GET, mail):
        print('called')
        zip_file = zipfile.ZipFile(os.path.join(settings.MEDIA_ROOT, 'temp', f'export_{mail}.zip'), "w")
        contexts = Act.generate_acts_by_notifies(request_GET)
        for context in contexts:
            doc = DocxTemplate(os.path.join(settings.MEDIA_ROOT, 'templates', 'act_backend.docx'))
            doc.render(context)
            f = io.BytesIO()
            doc.save(f)
            org = context['organization']
            zip_file.writestr(org.name.replace('/', '') + ', ' + org.inn + '.docx', f.getvalue())
        zip_file.close()