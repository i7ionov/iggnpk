from datetime import datetime

import xlrd
from dictionaries.models import Organization, Address, House
from capital_repair import models


def notifies():
    rb = xlrd.open_workbook('C:\\Users\\User\\Desktop\\Code\\iggnpk\\iggnpk\\notify.xlsx')
    sheet = rb.sheet_by_index(0)
    for rownum in range(5, sheet.nrows):
        bank, created = models.CreditOrganization.objects.get_or_create()


"""
        notify = models.Notify()
        notify.date = datetime.strptime(sheet.cell(rownum, 1).value, '%d.%m.%Y')
        try:
            street = sheet.cell(rownum, 4).value
            street = street.replace('Революции', 'ул. Революции').\
                replace('Максима Горького', 'ул. Максима Горького').\
                replace('Бульвар Гагарина', 'б-р Гагарина').\
                replace('Проспект Парковый', 'пр-кт Парковый'). \
                replace('Проспект Декабристов', 'пр-кт Декабристов'). \
                replace('Генерала Панфилова', 'Панфилова'). \
                strip()
            if (sheet.cell(rownum, 2).value == 'г. Пермь'):
                try:
                    addr = Address.objects.get(city='г. Пермь', street='ул. ' + street)
                except:
                    addr = Address.objects.get(city='г. Пермь', street__contains=street)
            else:
                try:
                    addr = Address.objects.get(area=sheet.cell(rownum, 2).value, city=sheet.cell(rownum, 3).value, street='ул. '+street)
                except:
                    addr = Address.objects.get(city=sheet.cell(rownum, 3).value,
                                               street__contains=street)

            notify.house, created = House.objects.get_or_create(address_id=addr.id, number=sheet.cell(rownum, 5).value)
        except:
            pass

        org, created = Organization.objects.get_or_create(inn=sheet.cell(rownum, 10).value)
        if created:
            org.name = sheet.cell(rownum, 9).value
            org.ogrn = 'нет'

        bank, created = models.CreditOrganization.objects.get_or_create(name=sheet.cell(rownum, 15).value,
                                                                        inn=sheet.cell(rownum, 17).value,
                                                                        bik=sheet.cell(rownum, 19).value)
        branch, created = models.Branch.objects.get_or_create(address=sheet.cell(rownum, 16).value, 
                                                              kpp=sheet.cell(rownum, 18).value)
        notify.credit_organization_branch = branch

        print(sheet.cell(rownum, 0).value)
        print(addr.street)
        print(street)
"""
