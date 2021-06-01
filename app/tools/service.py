class ServiceException(Exception):
    errors = None

    def __init__(self, errors):
        self.errors = errors


def upd_foreign_key(field, data, instance, model):
    """ Обновляет поле field в объекте instance, если это поле было передано в словаре data.
        Где поле field это ForeignKey к модели model.
        Если поле не передано, возвращает предыдущее значение """
    if field in data:
        if instance is not None and instance.__getattribute__(field) is not None and data[field]['id'] == instance.__getattribute__(field).id:
            return instance.__getattribute__(field)
        return model.objects.get(id=data[field]['id'])
    else:
        if instance is None:
            raise ServiceException(f'Не указано поле {field}')
        return instance.__getattribute__(field)


def upd_many_to_many(field, data, instance, model):
    """ Обновляет поле field в объекте instance, если это поле было передано в словаре data.
        Где поле field это связь Many-To-Many к модели model.
        Если поле не передано, возвращает предыдущее значение """
    array = []
    if field in data:
        if data[field] != 'empty':
            for f in data[field]:
                array.append(model.objects.get(id=f['id']))
    elif instance:
        array = instance.__getattribute__(field).all()
    return array
