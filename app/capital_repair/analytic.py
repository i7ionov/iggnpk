import os
from datetime import date

import openpyxl
from django.db.models import Sum

from capital_repair.models import ContributionsInformation
from iggnpk import settings
from tools.date_tools import normalize_date
from tools.get_value import get_value


class CrReportItem:
    fields = {'total': None,
              'tsj': ['ТСЖ', 'ТСН'],
              'jk': ['ЖК', 'ЖСК'],
              'uk': ['УК', 'ИП'],
              'ro': ['РО']}

    def __init__(self, **params):
        for field in self.fields.keys():
            if field in params and params[field]:
                self.__setattr__(field, params[field])
            else:
                self.__setattr__(field, 0)

    def __sub__(self, other):
        for field in self.fields.keys():
            if self.__getattribute__(field) is None:
                self.__setattr__(field, 0)

            if other.__getattribute__(field) is None:
                other.__setattr__(field, 0)

        return CrReportItem(total=self.total-other.total,
                              tsj=self.tsj-other.tsj,
                              jk=self.jk-other.jk,
                              uk=self.uk-other.uk,
                              ro=self.ro-other.ro)


class CrReport:
    fields = ['assessed_contributions_total',
              'assessed_contributions_current',
              'received_contributions_total',
              'received_contributions_current',
              'delta_total',
              'funds_spent',
              'credit',
              'funds_on_special_deposit',
              'fund_balance']
    item_fields = {'total': None,
              'tsj': ['ТСЖ', 'ТСН'],
              'jk': ['ЖК', 'ЖСК'],
              'uk': ['УК', 'ИП'],
              'ro': ['РО']}
    assessed_contributions_total = {}
    assessed_contributions_current = {}
    received_contributions_total = {}
    received_contributions_current = {}
    delta_total = {}
    funds_spent = {}
    funds_spent_in_last_year = {}
    credit = {}
    funds_on_special_deposit = {}
    fund_balance = {}

    def __init__(self):
        for field in self.fields:
            for item_field in self.item_fields:
                self.__getattribute__(field)[item_field] = 0


def create_report(date_start, date_end):
    date_start = normalize_date(date_start)
    date_end = normalize_date(date_end)
    report = CrReport()
    query = ContributionsInformation.objects.filter(date__range=(date_start, date_end), status_id=3)
    for field in CrReport.fields:
        for item_field, value in CrReport.item_fields.items():
            if value:
                report.__getattribute__(field)[item_field] = query.filter(notify__organization__type__text__in=value) \
                    .aggregate(Sum(field))[field + '__sum']
            else:
            report.__getattribute__(field)[''] = query.aggregate(Sum(field))[field+'__sum']
        report.__getattribute__(field).tsj = query.filter(notify__organization__type__text__in=['ТСЖ', 'ТСН'])\
            .aggregate(Sum(field))[field+'__sum']
        report.__getattribute__(field).jk = query.filter(notify__organization__type__text__in=['ЖК', 'ЖСК']) \
            .aggregate(Sum(field))[field+'__sum']
        report.__getattribute__(field).uk = query.filter(notify__organization__type__text__in=['УК', 'ИП']) \
            .aggregate(Sum(field))[field+'__sum']
        report.__getattribute__(field).ro = query.filter(notify__organization__type__text__in=['РО']) \
            .aggregate(Sum(field))[field+'__sum']
    date_start = date(date.today().year-1, 1, 1)
    date_end = date(date.today().year-1, 12, 31)
    query = ContributionsInformation.objects.filter(date__range=(date_start, date_end), status_id=3)

    report.__getattribute__(field).total = query.aggregate(Sum(field))[field + '__sum']
    report.__getattribute__(field).tsj = query.filter(notify__organization__type__text__in=['ТСЖ', 'ТСН']) \
        .aggregate(Sum(field))[field + '__sum']
    report.__getattribute__(field).jk = query.filter(notify__organization__type__text__in=['ЖК', 'ЖСК']) \
        .aggregate(Sum(field))[field + '__sum']
    report.__getattribute__(field).uk = query.filter(notify__organization__type__text__in=['УК', 'ИП']) \
        .aggregate(Sum(field))[field + '__sum']
    report.__getattribute__(field).ro = query.filter(notify__organization__type__text__in=['РО']) \
        .aggregate(Sum(field))[field + '__sum']

    return report


def report_to_excel(report):
    wb = openpyxl.load_workbook(os.path.join(settings.MEDIA_ROOT, 'templates', 'cr_report.xlsx'))
    ws = wb.worksheets[0]
    a = report.assessed_contributions_total
    b = report.assessed_contributions_current
    c = report.received_contributions_total
    d = report.received_contributions_current
    e = report.delta_total
    f = report.funds_spent
    g = report.credit
    h = report.funds_on_special_deposit
    i = report.fund_balance

    j = a - b
    k = c - d
    l = f - CrReportItem() # тут должны быть данные за прошлый год

    ws.cell(22, 7).value = j.total / 1000000
    ws.cell(24, 7).value = j.ro / 1000000
    ws.cell(25, 7).value = j.tsj / 1000000
    ws.cell(26, 7).value = j.jk / 1000000
    ws.cell(27, 7).value = j.uk / 1000000

    ws.cell(28, 7).value = k.total / 1000000
    ws.cell(30, 7).value = k.ro / 1000000
    ws.cell(31, 7).value = k.tsj / 1000000
    ws.cell(32, 7).value = k.jk / 1000000
    ws.cell(33, 7).value = k.uk / 1000000

    ws.cell(34, 7).value = (k.total*100)/j.total
    ws.cell(36, 7).value = (k.ro*100)/j.ro
    ws.cell(37, 7).value = (k.tsj*100)/j.tsj
    ws.cell(38, 7).value = (k.jk*100)/j.jk
    ws.cell(39, 7).value = (k.uk*100)/j.uk

    ws.cell(40, 7).value = b.total / 1000000
    ws.cell(42, 7).value = b.ro / 1000000
    ws.cell(43, 7).value = b.tsj / 1000000
    ws.cell(44, 7).value = b.jk / 1000000
    ws.cell(45, 7).value = b.uk / 1000000

    ws.cell(46, 7).value = d.total / 1000000
    ws.cell(48, 7).value = d.ro / 1000000
    ws.cell(49, 7).value = d.tsj / 1000000
    ws.cell(50, 7).value = d.jk / 1000000
    ws.cell(51, 7).value = d.uk / 1000000

    ws.cell(52, 7).value = (d.total*100)/b.total
    ws.cell(54, 7).value = (d.ro*100)/b.ro
    ws.cell(55, 7).value = (d.tsj*100)/b.tsj
    ws.cell(56, 7).value = (d.jk*100)/b.jk
    ws.cell(57, 7).value = (d.uk*100)/b.uk

    ws.cell(59, 7).value = (a.total - i.total - l.total) / 1000000
    ws.cell(61, 7).value = (a.ro - i.ro - l.ro) / 1000000
    ws.cell(62, 7).value = (a.tsj - i.tsj - l.tsj) / 1000000
    ws.cell(63, 7).value = (a.jk - i.jk - l.jk) / 1000000
    ws.cell(64, 7).value = (a.uk -i.uk - l.uk) / 1000000

    ws.cell(66, 7).value = (i.total - d.total + l.total) / 1000000
    ws.cell(67, 7).value = (i.ro - d.ro + l.ro) / 1000000
    ws.cell(68, 7).value = (i.tsj - d.tsj + l.tsj) / 1000000
    ws.cell(69, 7).value = (i.jk - d.jk + l.jk) / 1000000
    ws.cell(70, 7).value = (i.uk - d.uk + l.uk) / 1000000

    ws.cell(71, 7).value = d.total / 1000000
    ws.cell(72, 7).value = d.ro / 1000000
    ws.cell(73, 7).value = d.tsj / 1000000
    ws.cell(74, 7).value = d.jk / 1000000
    ws.cell(75, 7).value = d.uk / 1000000

    ws.cell(76, 7).value = l.total / 1000000
    ws.cell(77, 7).value = l.ro / 1000000
    ws.cell(78, 7).value = l.tsj / 1000000
    ws.cell(79, 7).value = l.jk / 1000000
    ws.cell(80, 7).value = l.uk / 1000000

    ws.cell(81, 7).value = 0
    ws.cell(82, 7).value = 0
    ws.cell(83, 7).value = 0
    ws.cell(84, 7).value = 0
    ws.cell(85, 7).value = 0

    ws.cell(86, 7).value = i.total / 1000000
    ws.cell(87, 7).value = i.ro / 1000000
    ws.cell(88, 7).value = i.tsj / 1000000
    ws.cell(89, 7).value = i.jk / 1000000
    ws.cell(90, 7).value = i.uk / 1000000

    wb.save(os.path.join(settings.MEDIA_ROOT, 'temp', 'cr_report.xlsx'))

create_report()
