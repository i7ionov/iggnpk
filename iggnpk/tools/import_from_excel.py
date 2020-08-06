from datetime import datetime

import xlrd
from dictionaries.models import Organization, Address, House
from capital_repair import models


def notifies():
    rb = xlrd.open_workbook('C:\\Users\\User\\Desktop\\Code\\iggnpk\\iggnpk\\notify.xlsx')
    sheet = rb.sheet_by_index(0)
    for rownum in range(5, sheet.nrows):


        notify = models.Notify()
        try:
            notify.date = datetime.strptime(sheet.cell(rownum, 1).value, '%d.%m.%Y')
        except TypeError: pass
        street = sheet.cell(rownum, 4).value.strip()
        print(sheet.cell(rownum, 0).value)
        print(sheet.cell(rownum, 2).value)
        print(sheet.cell(rownum, 3).value)
        print(street)

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

        print(street)
        city = sheet.cell(rownum, 3).value.replace('Ё', 'Е')\
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
        print(city)
        if city == 'п. Полазна':
            area = 'Добрянский'
        addr = Address.objects.filter(area__contains=area, city=city, street=street).first()




        print(addr.street)

"""     
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

        
"""
