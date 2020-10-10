import os
from datetime import datetime
import requests
import xlrd

from capital_repair.models import Status
from dictionaries.models import Organization, Address, House, OrganizationType
from capital_repair import models
from iggnpk import settings


def cut_value(val, comment):
    if '(' in str(val):
        return val[:val.find('(')].strip(), comment + ": " + val[val.find('('):].strip() + ". "
    else:
        if type(val) == str:
            val = val.strip()
        return val, ''

def houses():

    f = open(os.path.join(settings.MEDIA_ROOT, 'temp', 'reestr_licensing.xlsx'), "wb")  # открываем файл для записи, в режиме wb
    ufr = requests.get("https://iggn.permkrai.ru/download.php?id=1621")  # делаем запрос
    f.write(ufr.content)  # записываем содержимое в файл; как видите - content запроса
    f.close()
    rb = xlrd.open_workbook(os.path.join(settings.MEDIA_ROOT, 'temp', 'reestr_licensing.xlsx'))
    sheet = rb.sheet_by_index(1)
    for rownum in range(6, sheet.nrows):
        if sheet.cell(rownum, 0).value == '':
            continue
        print(sheet.cell(rownum, 0).value)
        # адрес дома
        number = str(sheet.cell(rownum, 6).value).strip().lower().replace('.0', '')
        street, comm = cut_value(sheet.cell(rownum, 5).value, '')
        if 'Блочная' in street:
            street = 'ул. Блочная'
        city = sheet.cell(rownum, 4).value.strip()
        if street == 'ул. К.Заслонова' and city == 'пгт. Широковский':
            street = 'ул. К. Заслонова'
        if street == 'ул. Новоселовой':
            street = 'ул. Новоселова'
        if street == '' and city == 'г. Пермь':
            continue
        area = sheet.cell(rownum, 3).value.strip()
        if area == 'льская' and city == 'г. Березники':
            area = 'Березниковский городской округ'

        print(f'{area} {city} {street} {number}')
        addr = Address.objects.filter(area__contains=area, city=city, street=street).first()
        house, created = House.objects.get_or_create(address_id=addr.id, number=number)
        # организация
        inn = str(sheet.cell(rownum, 1).value).strip().replace('.0', '')
        name = sheet.cell(rownum, 2).value.strip()
        org, created = Organization.objects.get_or_create(inn=inn)
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
            notify.date = get_datetime(sheet.cell(rownum, 1).value)
        except TypeError: pass
        street = sheet.cell(rownum, 6).value.strip()

        street = street.replace('ул. Садовое кольцо', 'ул. Садовое Кольцо').replace('1-я Колхозная', 'Колхозная 1-я').\
            replace('Братьев Вагановых', 'Вагановых'). \
            replace('января', 'Января'). \
            replace('Войкого', 'Войкова'). \
            replace('Ириловская - Набережная', 'Ириловская Набережная'). \
            replace('ул. Парковый', 'пр-кт Парковый'). \
            replace('ул. Б.Хмельницкого', 'ул. Богдана Хмельницкого'). \
            replace('ул. Н.Быстрых', 'ул. Николая Быстрых'). \
            replace('ул. Сведлова', 'ул. Свердлова'). \
            replace("""
(Луначарского)""", '').replace('ё', 'е')
        if '/' in street:
            street = street[:street.find('/')].strip()
        area = str(sheet.cell(rownum, 2).value).replace('г. Соликамск', 'Соликамский').\
            replace('г. Березники', 'Березниковский'). \
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
            .replace('"Город Губаха"', 'Городской округ «Город Губаха»') \
            .strip()

        if city == 'п. Полазна':
            area = 'Добрянский'
        print(f'{area} {city} {street}')
        addr = Address.objects.filter(area__contains=area, city=city, street=street).first()
        notify.house, created = House.objects.get_or_create(address_id=addr.id, number=str(sheet.cell(rownum, 7).value).strip().lower().replace('.0', ''))
        temp, com = cut_value(sheet.cell(rownum, 16).value, 'Дата включения в программу КР')
        notify.comment2 += com
        notify.house.date_of_inclusion = get_datetime(temp)


        temp, com = cut_value(sheet.cell(rownum, 15).value, 'Включен в программу КР')
        notify.comment2 += com
        notify.house.included_in_the_regional_program = temp == 'Включен'
        notify.house.save()

        org, created = Organization.objects.get_or_create(inn=str(sheet.cell(rownum, 12).value).strip().replace('.0', ''))
        if created:
            org.name = sheet.cell(rownum, 11).value.strip()
            org.ogrn = 'нет'
            org.type = OrganizationType.objects.get(text=sheet.cell(rownum, 10).value.strip())
        org.save()
        notify.organization = org
        notify.comment2 = notify.comment2 + " " + sheet.cell(rownum, 13).value

        name, com = cut_value(sheet.cell(rownum, 17).value, 'Банк')
        notify.comment2 += com

        inn, com = cut_value(sheet.cell(rownum, 19).value, 'ИНН')
        notify.comment2 += com

        bik, com = cut_value(sheet.cell(rownum, 21).value, 'БИК')
        notify.comment2 += com
        bank = models.CreditOrganization.objects.get(inn=str(inn).replace('.0', ''))
        notify.bank = bank

        temp, com = cut_value(sheet.cell(rownum, 23).value, 'Номер спец. счета')
        notify.comment2 += com
        notify.account_number = temp

        temp, com = cut_value(sheet.cell(rownum, 24).value, 'Дата открытия')
        notify.comment2 += com
        notify.account_opening_date = get_datetime(temp)
        try:
            monthly_contribution_amount = sheet.cell(rownum, 26).value.strip().split(' ')[0] + '.' + sheet.cell(rownum, 26).value.strip().split(' ')[2]
            notify.monthly_contribution_amount = float(monthly_contribution_amount)
        except IndexError:
            notify.monthly_contribution_amount = 0
        notify.protocol_details = sheet.cell(rownum, 27).value

        if sheet.cell(rownum, 28).value == 'Исключен':
            notify.status = Status.objects.get(id=4)
        else:
            notify.status = Status.objects.get(id=3)

        notify.date_of_exclusion = get_datetime(sheet.cell(rownum, 29).value)
        notify.account_closing_date = get_datetime(sheet.cell(rownum, 30).value)
        notify.ground_for_exclusion = sheet.cell(rownum, 31).value
        notify.source_of_information = sheet.cell(rownum, 32).value
        notify.save()


def get_datetime(temp):
    try:
        if type(temp) == float:
            return datetime.utcfromtimestamp((temp - 25569) * 86400.0)
        elif '.' in temp:
            return datetime.strptime(temp, '%d.%m.%Y')
        else:
            return datetime.strptime(temp, '%d %m %Y')
    except ValueError:
        pass
    return None