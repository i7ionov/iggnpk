from enum import Enum

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from dictionaries.models import House, Organization, File
from simple_history.models import HistoricalRecords


class CreditOrganization(models.Model):
    name = models.CharField(max_length=100, verbose_name='Наименование кредитной организации')
    inn = models.CharField(max_length=100, blank=True, verbose_name='ИНН')
    allow_to_select = models.BooleanField(blank=True, default=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name


class Branch(models.Model):
    credit_organization = models.ForeignKey(CreditOrganization, on_delete=models.SET_NULL, null=True, verbose_name='Кредитная рганизация',
                                            blank=True)
    address = models.CharField(max_length=100, verbose_name='Адрес')
    kpp = models.CharField(max_length=100, blank=True, verbose_name='КПП')
    bik = models.CharField(max_length=100, blank=True, verbose_name='БИК')
    correspondent_account = models.CharField(max_length=30, blank=True, verbose_name='Корреспондентский счет')
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.credit_organization.name} {self.address}'


class Status(models.Model):
    text = models.CharField(max_length=30, blank=True, verbose_name='Статус')


class Notify(models.Model):
    STATUSES = (
        ('1', 'Editing'),
        ('2', 'Approving'),
        ('3', 'Approved'),
    )
    date = models.DateField(verbose_name='Дата внесения записи', null=True, blank=True, default=None)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, verbose_name='Организация',
                                     blank=True, default=None)
    house = models.ForeignKey(House, on_delete=models.SET_NULL, null=True, verbose_name='Дом',
                              blank=True)
    credit_organization_branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True,
                                            verbose_name='Кредитная организация',
                                            blank=True)
    bank = models.ForeignKey(CreditOrganization, on_delete=models.SET_NULL, null=True,
                                                   verbose_name='Кредитная организация',
                                                   blank=True)
    account_number = models.CharField(max_length=300, blank=True, verbose_name='Номер счета')
    account_opening_date = models.DateField(verbose_name='Дата открытия счета', blank=True, null=True)
    monthly_contribution_amount = models.FloatField(verbose_name='Ежемесячный размер взноса')
    protocol_details = models.CharField(max_length=1000, verbose_name='Реквизиты протокола')
    comment = models.TextField(verbose_name='Комментарий', null=True, blank=True)
    comment2 = models.TextField(verbose_name='Комментарий', null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, verbose_name='Статус',
                               blank=True, default=None)
    date_of_exclusion = models.DateField(verbose_name='Дата исключения', null=True, blank=True)
    account_closing_date = models.DateField(verbose_name='Дата закрытия счета', null=True, blank=True)
    ground_for_exclusion = models.CharField(max_length=1000, verbose_name='Основание для исключения', null=True, blank=True)
    source_of_information = models.CharField(max_length=1000, verbose_name='Источник получения информации', null=True, blank=True)

    files = models.ManyToManyField(File)
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.date}, № {self.id}'

    class Meta:
        permissions = (("view_comment2", 'view comment2'),)


class ContributionsInformation(models.Model):
    date = models.DateField(verbose_name='Дата внесения записи', null=True, blank=True, default=None)
    notify = models.ForeignKey(Notify, on_delete=models.SET_NULL, null=True, verbose_name='Уведомление',
                                     blank=True, default=None)
    assessed_contributions_total = models.DecimalField(null=True, blank=True, verbose_name='Начислено взносов, всего', max_digits=15, decimal_places=2)
    assessed_contributions_current = models.DecimalField(null=True, blank=True, verbose_name='Начислено взносов, за текущий период', max_digits=15, decimal_places=2)
    received_contributions_total = models.DecimalField(null=True, blank=True, verbose_name='Поступило взносов, всего', max_digits=15, decimal_places=2)
    received_contributions_current = models.DecimalField(null=True, blank=True, verbose_name='Поступило взносов, за текущий период', max_digits=15, decimal_places=2)
    delta_total = models.DecimalField(null=True, blank=True, verbose_name='Задолженность (+), переплата (-), всего', max_digits=15, decimal_places=2)
    funds_spent = models.DecimalField(null=True, blank=True, verbose_name='Израсходовано средств', max_digits=15, decimal_places=2)
    credit = models.DecimalField(null=True, blank=True, verbose_name='Сведения о заключении договора займа ', max_digits=15, decimal_places=2)
    funds_on_special_deposit = models.DecimalField(null=True, blank=True, verbose_name='Сведения о размере средств, находящихся на специальном депозите ', max_digits=15, decimal_places=2)
    fund_balance = models.DecimalField(null=True, blank=True, verbose_name='Остаток средств', max_digits=15, decimal_places=2)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, verbose_name='Статус',
                               blank=True, default=None)
    comment = models.TextField(verbose_name='Комментарий', null=True, blank=True)
    comment2 = models.TextField(verbose_name='Комментарий', null=True, blank=True)
    files = models.ManyToManyField(File)
    history = HistoricalRecords()