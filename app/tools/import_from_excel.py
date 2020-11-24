import os
from datetime import datetime
import requests
import xlrd

from capital_repair.models import Status, Notify
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


def swap_number_in_street(street):
    """Ставит порядковое число в улице в конец. Например, если было пер. 1-й Короткий, то будет пер. Короткий 1-й """
    temp = street.split(' ')
    if len(temp) < 3:
        return street
    # меняем только в том числе, если второе слово в названии улицы содержит число и тире
    if any(map(str.isdigit, temp[1])) and '-' in temp[1]:
        return temp[0] + ' ' + temp[2] + ' ' + temp[1]
    return street


def safe_address_delete(id):
    try:
        Address.objects.get(id=id).delete()
    except Address.DoesNotExist:
        pass


def patch():
    """Нужно будет потом далить после патча"""
    for id in ['2696', '90', '11457', '11675', '11675', '11677', '14929', '11457', '11675', '15320']:
        safe_address_delete(id)

    for a in Address.objects.filter(area='Верещагинский муниципальный район', place='Зюкайское сельское поселение',
                                    city='п. Зюкайка'):
        a.delete()
    for a in Address.objects.filter(city__icontains='Липовая'):
        a.city = a.city.replace(' 1', '').replace(' 2', '')
        a.save()

    for a in Address.objects.all():
        a.city = normalize_city(a.city)
        a.street = normalize_street(a.street)
        a.save()


def normalize_street(street):
    street = street.split('/')[0].strip() # отсекаем вторую часть улицы вида "ул. Большевистская /Матросова, 18"

    street = street.replace('Максима ', '').replace('М.', '').replace('ул. Р. Люксембург', 'ул. Розы Люксембург') \
        .replace('К.Маркса', 'Карла Маркса').replace('К. Маркса', 'Карла Маркса') \
        .replace('Александра Матросова', 'Матросова').replace('А.Матросова', 'Матросова').replace('А. Матросова',
                                                                                                  'Матросова') \
        .replace('Константина Заслонова', 'Заслонова').replace('К.Заслонова', 'Заслонова').replace('К. Заслонова',
                                                                                                   'Заслонова') \
        .replace('Олега Кошевого', 'Кошевого').replace('О.Кошевого', 'Кошевого').replace('О. Кошевого',
                                                                                         'Кошевого') \
        .replace('Павлика Морозова', 'Морозова').replace('П.Морозова', 'Морозова').replace('П. Морозова',
                                                                                           'Морозова') \
        .replace('Л.Чайкиной', 'Лизы Чайкиной').replace('Л. Чайкиной', 'Лизы Чайкиной') \
        .replace('Ф.Энгельса', 'Энгельса').replace('Ф. Энгельса', 'Энгельса') \
        .replace('В.И. Кузнецова', 'Кузнецова').replace('Н.Кузнецова', 'Кузнецова') \
        .replace('Кузнецова В.И.', 'Кузнецова').replace('Разведчика Н.И.Кузнецова', 'Кузнецова') \
        .replace('Николая Кузнецова', 'Кузнецова') \
        .replace('Александра Невского', 'Невского').replace('А.Невского', 'Невского') \
        .replace('ул. Розы Землячки', 'ул. Розалии Землячки') \
        .replace('ул. Р.Люксембург', 'ул. Розы Люксембург') \
        .replace('Г.Богомягкова', 'Богомягкова').replace('Богомягкова Степана Николаевича', 'Богомягкова') \
        .replace('Сергея Корнеева', 'Корнеева') \
        .replace('ул. 8-е марта', 'ул. 8 Марта') \
        .replace('ул. 8-е Марта', 'ул. 8 Марта') \
        .replace('ул. 8е Марта', 'ул. 8 Марта') \
        .replace('ул. Ветеранов Войны', 'ул. Ветеранов войны') \
        .replace('ул. Газеты Правда', 'ул. им. газ. Правда') \
        .replace('Газеты Правды', 'Правды') \
        .replace('тракт Ленский', 'Ленский тракт') \
        .replace('тракт Плехановский', 'Плехановский тракт') \
        .replace('ул. Шпалозавод', 'п. Шпалозавода') \
        .replace('ул. Иренская набережная', 'Иренская набережная') \
        .replace('ул. Ириловская набережная', 'Ириловская набережная') \
        .replace('ул. Виталия Онькова', 'ул. Онькова Виталия') \
        .replace('ул. Братьев Вагановых', 'ул. Вагановых') \
        .replace('ул. Татьяны Барамзиной', 'ул. Барамзиной Татьяны') \
        .replace('ул. Володи Дубинина', 'ул. Дубинина') \
        .replace('ул. А.И. Осокина', 'ул. Осокина А.И.') \
        .replace('П.Осипенко', 'Полины Осипенко') \
        .replace('ул. Лаврова', 'ул. Льва Лаврова') \
        .replace('ул. ПМС-14', 'ул. ОПМС-14') \
        .replace('ул. 9-го Мая', 'ул. 9 Мая') \
        .replace('40-летия', '40 лет') \
        .replace('тракт Сибирский', 'Сибирский тракт') \
        .replace('пр-т', 'пр-кт') \
        .replace('пр-д', 'проезд') \
        .replace('ё', 'е').replace('мкр ', 'мкр. ')

    if street in ['пер. 1-й Дубровский', 'пер. 2-й Дубровский', 'пер. 1-й Еловский', 'проезд 1-й Павловский',
                  'ул. 13-я Линия', 'ул. 1-я Ипподромная', 'ул. 1-я Колхозная', 'ул. 1-я Красноармейская',
                  'ул. 1-я Нейвинская', 'ул. 2-я Гамовская', 'ул. 2-я Казанцевская', 'ул. 2-я Пограничная', 'ул. 4-я Запрудская',
                  'ул. 5-я Каховская', 'ул. 1-я Железнодорожная']:
        street = swap_number_in_street(street)
    if 'Пятилетки' in street:
        street = street.replace('-й', '').replace('-ой', '')
    if street.strip() == '-':
        street = ''
    return street


def normalize_city(city):
    city = city.replace('ё', 'е').replace('р.п.', 'п.').replace('рп ', 'п. ').replace('пгт ', 'п. ').replace('ст.п.', 'п.') \
        .replace('ст.п', 'п.').replace('п/ст ', 'п. ').replace('п. ст. ', 'п. ').replace('рп. ', 'п. ') \
        .replace('п. Южный Коспашский', 'п. Южный-Коспашский')
    return city


def regional_program():
    f = open(os.path.join(settings.MEDIA_ROOT, 'temp', 'regional_program.xlsx'),
             "wb+")
    ufr = requests.get("https://fond59.ru/upload/iblock/a47/a476b04ebb126fe72eac416ef34fd80c.xlsx")
    f.write(ufr.content)
    f.close()
    for h in House.objects.all():
        h.included_in_the_regional_program = False
        h.save()

    rb = xlrd.open_workbook(os.path.join(settings.MEDIA_ROOT, 'temp', 'regional_program.xlsx'))
    sheet = rb.sheet_by_index(1)
    for rownum in range(3, sheet.nrows):
        if sheet.cell(rownum, 1).value == '':
            continue
        area = str(sheet.cell(rownum, 1).value).strip()
        area = area.replace('Березники', 'Березниковский').replace('Пермь', 'Пермский').replace('Лысьва', 'Лысьвенский')
        city = str(sheet.cell(rownum, 2).value).strip()
        city = city.replace('д. Ваньки', 'с. Ваньки').replace('с. Большой Букор','д. Большой Букор')\
            .replace('Белоборово','Белобородово')
        city = normalize_city(city)
        street = str(sheet.cell(rownum, 3).value).strip()
        street = normalize_street(street)

        city = city.replace('ЗАТО Звездный', 'пгт. Звездный').replace('д. Берег Камы (Юго-Камское г/п)', 'д. Берег Камы')
        if city == 'г. Усолье' or city == 'п. Железнодорожный' or city == 'с. Пыскор':
            area = 'Усольский муниципальный район'
        elif city == 'г. Чусовой, п. Лямино':
            city = 'п. Лямино'
        elif 'п. Новые Ляды' in city:
            city = 'г. Пермь'
            street = street.replace('ул. 40-летия Победы', 'ул. 40 лет Победы (Новые Ляды)')\
                .replace('ул. Веселая', 'ул. Веселая (Новые Ляды)')\
                .replace('ул. Мира', 'ул. Мира (Новые Ляды)') \
                .replace('ул. Молодежная', 'ул. Молодежная (Новые Ляды)') \
                .replace('ул. Островского', 'ул. Островского (Новые Ляды)')\
                .replace('ул. Чусовская', 'ул. Чусовская (Новые Ляды)')
        elif city == 'с. Григорьевское':
            street = street.replace('пл. Советская', 'ул. Советская')
        elif city == 'п. Октябрьский':
            street = street.replace('ул. Крупской', 'ул. Крупская')
        elif city == 'г. Чердынь':
            street = street.replace('пер. Сарапулова', 'ул. Сарапулова').replace('мкр. АК-5', 'ул. АТК')



        number = str(sheet.cell(rownum, 4).value).strip().replace('.0', '').lower()
        try:
            address = Address.objects.get(area__icontains=area, city__iexact=city, street__iexact=street)
            house = House.objects.get(address_id=address.id, number__iexact=number)
            house.included_in_the_regional_program = True
            house.save()
        except (Address.DoesNotExist, Address.MultipleObjectsReturned):
            print(f'Not Founded {rownum} {area} {city} {street}')
        except House.DoesNotExist:
            print(f'Not Founded {rownum} {area} {city} {street} {number}')
        except House.MultipleObjectsReturned:
            print(f'Multiple Founded {rownum} {area} {city} {street} {number}')


def houses():
    f = open(os.path.join(settings.MEDIA_ROOT, 'temp', 'reestr_licensing.xlsx'),
             "wb+")  # открываем файл для записи, в режиме wb
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
        street = normalize_street(street)
        if 'Блочная' in street:
            street = 'ул. Блочная'
        city = normalize_city(sheet.cell(rownum, 4).value.strip())
        city = city.replace('р.п.', 'п.')
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
        if sheet.cell(rownum, 8).value == ' ' or sheet.cell(rownum, 8).value == '':
            inn = str(sheet.cell(rownum, 1).value).strip().replace('.0', '')
            name = sheet.cell(rownum, 2).value.strip()
            org, created = Organization.objects.get_or_create(inn=inn)
            org.name = name
            org.save()
            house.organization = org
            house.save()
        else:
            house.organization = None
            house.save()

        for n in Notify.objects.filter(house=house, status_id=3):
            if sheet.cell(rownum, 8).value == ' ' or sheet.cell(rownum, 8).value == '':
                n.same_organization_in_license_registry = n.organization == org
                n.save()
            else:
                n.same_organization_in_license_registry = None
                n.save()


def notifies():
    rb = xlrd.open_workbook('C:\\Users\\User\\Desktop\\Code\\iggnpk\\iggnpk\\notify.xlsx')
    sheet = rb.sheet_by_index(0)
    for rownum in range(5, sheet.nrows):

        print(sheet.cell(rownum, 0).value)
        notify = models.Notify()
        notify.comment2 = ''
        try:
            notify.date = get_datetime(sheet.cell(rownum, 1).value)
        except TypeError:
            pass
        street = sheet.cell(rownum, 6).value.strip()

        street = street.replace('ул. Садовое кольцо', 'ул. Садовое Кольцо').replace('1-я Колхозная', 'Колхозная 1-я'). \
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
        area = str(sheet.cell(rownum, 2).value).replace('г. Соликамск', 'Соликамский'). \
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

        city = sheet.cell(rownum, 4).value.replace('Ё', 'Е') \
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
        notify.house, created = House.objects.get_or_create(address_id=addr.id, number=str(
            sheet.cell(rownum, 7).value).strip().lower().replace('.0', ''))
        temp, com = cut_value(sheet.cell(rownum, 16).value, 'Дата включения в программу КР')
        notify.comment2 += com
        notify.house.date_of_inclusion = get_datetime(temp)

        temp, com = cut_value(sheet.cell(rownum, 15).value, 'Включен в программу КР')
        notify.comment2 += com
        notify.house.included_in_the_regional_program = temp == 'Включен'
        notify.house.save()

        org, created = Organization.objects.get_or_create(
            inn=str(sheet.cell(rownum, 12).value).strip().replace('.0', ''))
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
            monthly_contribution_amount = sheet.cell(rownum, 26).value.strip().split(' ')[0] + '.' + \
                                          sheet.cell(rownum, 26).value.strip().split(' ')[2]
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
