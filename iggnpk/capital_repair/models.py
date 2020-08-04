from enum import Enum

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from dictionaries.models import House, Organization, File


class CreditOrganization(models.Model):
    name = models.CharField(max_length=100, verbose_name='Наименование кредитной организации')
    inn = models.CharField(max_length=100, blank=True, verbose_name='ИНН')
    bik = models.CharField(max_length=100, blank=True, verbose_name='БИК')
    correspondent_account = models.CharField(max_length=30, blank=True, verbose_name='Корреспондентский счет')

    def __str__(self):
        return self.name


class Branch(models.Model):
    credit_organization = models.ForeignKey(CreditOrganization, on_delete=models.SET_NULL, null=True, verbose_name='Кредитная рганизация',
                                            blank=True)
    address = models.CharField(max_length=100, verbose_name='Адрес')
    kpp = models.CharField(max_length=100, blank=True, verbose_name='КПП')

    def __str__(self):
        return f'{self.credit_organization.name} {self.address}'


class NotifyStatus(models.Model):
    text = models.CharField(max_length=30, blank=True, verbose_name='Статус')


class Notify(models.Model):
    STATUSES = (
        ('1', 'Editing'),
        ('2', 'Approving'),
        ('3', 'Approved'),
    )
    date = models.DateField(verbose_name='Дата внесения записи', null=True,blank=True, default=None)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, verbose_name='Организация',
                                     blank=True, default=None)
    house = models.ForeignKey(House, on_delete=models.SET_NULL, null=True, verbose_name='Дом',
                              blank=True)
    credit_organization_branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True,
                                            verbose_name='Кредитная организация',
                                            blank=True)
    account_number = models.CharField(max_length=300, blank=True, verbose_name='Номер счета')
    account_opening_date = models.DateField(verbose_name='Дата открытия счета')
    monthly_contribution_amount = models.FloatField(verbose_name='Ежемесячный размер взноса')
    protocol_details = models.CharField(max_length=100, verbose_name='Реквизиты протокола')
    comment = models.TextField(verbose_name='Комментарий', null=True, blank=True)
    comment2 = models.TextField(verbose_name='Комментарий', null=True, blank=True)
    status = models.ForeignKey(NotifyStatus, on_delete=models.SET_NULL, null=True, verbose_name='Статус',
                                     blank=True, default=None)
    files = models.ManyToManyField(File)

    def __str__(self):
        return f'{self.date}, № {self.id}'

    class Meta:
        permissions = (("view_comment2", 'view comment2'),)
