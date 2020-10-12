from datetime import datetime, date
def get_value(item, field):
    """
    Метод позволяет получить строковое значение у объекта item, хранящееся в поле field.
    :param item: Объект
    :param field: Название поля, может быть в виде "nested_object.field" с любым уровнем вложения
    :return: Строковое значение поля
    """
    val = item
    for p in str(field).split('.'):
        if val is None:
            continue
        # print("От %s берем %s" % (val, p))
        val = val.__getattribute__(p)
    if val is None:
        return None
    return datetime_handler(val)


def datetime_handler(obj):
    """Приводит дату в формат %d.%m.%Y"""
    if isinstance(obj, (datetime, date)):
        return obj.strftime('%d.%m.%Y')
    else:
        return str(obj)