from datetime import datetime

import xlrd

from capital_repair.models import NotifyStatus
from dictionaries.models import Organization, Address, House, OrganizationType
from capital_repair import models


def cut_value(val, comment):
    if '(' in str(val):
        return val[:val.find('(')].strip(), comment + ": " + val[val.find('('):].strip() + ". "
    else:
        return val, ''

def houses():
    rb = xlrd.open_workbook('C:\\Users\\ivsemionov\\Desktop\\reestr_licensing.xlsx')
    sheet = rb.sheet_by_index(1)
    for rownum in range(6, sheet.nrows):
        print(sheet.cell(rownum, 0).value)
        # адрес дома
        number = str(sheet.cell(rownum, 6).value).strip()
        street = sheet.cell(rownum, 5).value.strip().replace('.0')
        city = sheet.cell(rownum, 4).value.strip()
        area = sheet.cell(rownum, 3).value.strip()
        print(f'{area} {city} {street} {number}')
        addr = Address.objects.filter(area__contains=area, city=city, street=street).first()
        house, created = House.objects.get_or_create(address_id=addr.id, number=number)
        # организация
        inn = str(sheet.cell(rownum, 1).value).strip()
        name = sheet.cell(rownum, 2).value.strip()
        org, created = Organization.objects.get_or_create(inn=inn)
        if created:
            org.name = name
            org.save()
        house.organization = org
        house.save()

def notifies():
    rb = xlrd.open_workbook('C:\\Users\\User\\Desktop\\Code\\iggnpk\\iggnpk\\notify.xlsx')
    sheet = rb.sheet_by_index(0)
    for rownum in range(5, sheet.nrows):

        print(sheet.cell(rownum, 0).value)
        notify = models.Notify()
        notify.comment2 = ''
        try:
            notify.date = datetime.strptime(sheet.cell(rownum, 1).value, '%d.%m.%Y')
        except TypeError: pass
        street = sheet.cell(rownum, 6).value.strip()

        if str(street).__contains__('Бульвар'):
            street = street.replace('Бульвар', 'б-р')
        elif str(street).__contains__('бульвар'):
            street = street.replace(' бульвар', '')
            street = 'б-р ' + street
        elif str(street).__contains__('Шоссе') and str(street) != 'Шоссейная':
            street = street.replace('Шоссе', 'ш.')
        elif str(street).__contains__('Проспект'):
            street = street.replace('Проспект', 'пр-кт')
        elif str(street).__contains__('пр-т'):
            street = street.replace('пр-т', 'пр-кт')
        elif str(street).__contains__(' проспект'):
            street = street.replace(' проспект', '')
            street = 'пр-кт ' + street
        elif str(street).__contains__('проспект'):
            street = street.replace('проспект', 'пр-кт')
        elif str(street).__contains__('пр.'):
            street = street.replace('пр.', 'пр-кт')
        elif str(street).__contains__('проезд'):
            street = street.replace(' проезд', '')
            street = 'проезд ' + street
        elif str(street).__contains__(' переулок'):
            street = street.replace(' переулок', '')
            street = 'пер. ' + street
        elif str(street).__contains__('переулок'):
            street = street.replace('переулок', 'пер.')
        elif str(street).__contains__('Пер.'):
            street = street.replace('Пер.', 'пер.')
        elif str(street).__contains__(' Набережная') or str(street).__contains__('пер.') \
                or str(street).__contains__(' тракт') or str(street) == '':
            pass
        else:
            street = 'ул. ' + street
        street = street.replace('ул. Садовое кольцо', 'ул. Садовое Кольцо').replace('1-я Колхозная', 'Колхозная 1-я').\
            replace('Братьев Вагановых', 'Вагановых'). \
            replace('Павлика Морозова', 'П. Морозова'). \
            replace('-я', '-ая'). \
            replace('января', 'Января'). \
            replace('КИМ', 'Ким'). \
            replace('Войкого', 'Войкова'). \
            replace('пр-кт Свердлова', 'ул. Свердлова'). \
            replace('Ириловская - Набережная', 'Ириловская Набережная'). \
            replace('ул. Парковый', 'пр-кт Парковый'). \
            replace('ул. Б.Хмельницкого', 'ул. Богдана Хмельницкого'). \
            replace('ул. Н.Быстрых', 'ул. Николая Быстрых'). \
            replace('ул. Веры Засулич', 'ул. В. Засулич'). \
            replace('ул. Сведлова', 'ул. Свердлова'). \
            replace("""
(Луначарского)""", '').replace('ё', 'е')
        if '/' in street:
            street = street[:street.find('/')].strip()
        area = str(sheet.cell(rownum, 2).value).replace('г. Соликамск', 'Соликамский').\
            replace('г. Березники', 'Березниковский'). \
            replace('ЗАТО Звездный', 'Городской округ ЗАТО Звездный'). \
            replace('г. Лысьва', 'Лысьвенский'). \
            replace('г. Кунгур', 'Кунгурский'). \
            replace('г. Чайковский', 'Чайковский'). \
            replace('г. Оханск', 'Оханск'). \
            replace('г. Кудымкар', 'Кудымкарский'). \
            replace('Пермский район', 'Пермский'). \
            replace('г. Губаха', 'Городской округ «Город Губаха»'). \
            replace('г. Пермь', 'Пермский'). \
            replace('г.Пермь', 'Пермский'). \
            replace('Пермский край', '')

        city = sheet.cell(rownum, 4).value.replace('Ё', 'Е')\
            .replace('пос. Железнодорожный', 'п. Железнодорожный') \
            .replace('д. Усть-Сыны', 'с. Усть-Сыны') \
            .replace('п. Звездный', 'пгт. Звездный') \
            .replace('г.Пермь', 'г. Пермь') \
            .replace('г.Красновишерск', 'г. Красновишерск') \
            .replace('д.Кондратово', 'д. Кондратово') \
            .replace('пос.Новые Ляды', 'п. Новые Ляды') \
            .replace('г.Чайковский', 'г. Чайковский') \
            .replace('г.Краснокамск', 'г. Краснокамск') \
            .replace('пгт.Павловский', 'п. Павловский') \
            .replace('ст. ', 'ст.п ') \
            .strip()

        if city == 'п. Полазна':
            area = 'Добрянский'
        addr = Address.objects.filter(area__contains=area, city=city, street=street).first()
        notify.house, created = House.objects.get_or_create(address_id=addr.id, number=sheet.cell(rownum, 7).value)
        temp, com = cut_value(sheet.cell(rownum, 16).value, 'Дата включения в программу КР')
        notify.comment2 += com

        try:
            notify.house.date_of_inclusion = datetime.strptime(temp, '%d.%m.%Y')
        except ValueError:
            pass

        temp, com = cut_value(sheet.cell(rownum, 15).value, 'Включен в программу КР')
        notify.comment2 += com
        notify.house.included_in_the_regional_program = temp == 'Включен'
        notify.house.save()

        org, created = Organization.objects.get_or_create(inn=str(sheet.cell(rownum, 12).value).strip())
        if created:
            org.name = sheet.cell(rownum, 11).value.strip()
            org.ogrn = 'нет'
            org.type = OrganizationType.objects.get(text=sheet.cell(rownum, 10).value.strip())
        org.save()
        notify.comment2 = notify.comment2 + " " + sheet.cell(rownum, 13).value

        name, com = cut_value(sheet.cell(rownum, 17).value, 'Банк')
        notify.comment2 += com

        inn, com = cut_value(sheet.cell(rownum, 19).value, 'ИНН')
        notify.comment2 += com

        bik, com = cut_value(sheet.cell(rownum, 21).value, 'БИК')
        notify.comment2 += com

        bank = models.CreditOrganization.objects.get(inn=inn)
        notify.bank = bank

        notify.account_number = sheet.cell(rownum, 23).value

        opening_date, com = cut_value(sheet.cell(rownum, 24).value, 'Дата открытия')
        notify.comment2 += com
        notify.account_opening_date = opening_date

        monthly_contribution_amount = sheet.cell(rownum, 26).value.split(' ')[0] + '.' + sheet.cell(rownum, 26).value.split(' ')[3]
        notify.monthly_contribution_amount = float(monthly_contribution_amount)

        notify.protocol_details = sheet.cell(rownum, 27).value

        if sheet.cell(rownum, 28).value == 'Исключен':
            notify.status = NotifyStatus.objects.get(id=4)
        else:
            notify.status = NotifyStatus.objects.get(id=3)


