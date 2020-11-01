def upd_foreign_key(field, data, instance, model):
    if field in data:
        if instance.__getattribute__(field) is not None and data[field]['id'] == instance.__getattribute__(field).id:
            return instance.__getattribute__(field)
        return model.objects.get(id=data[field]['id'])
    else:
        return instance.__getattribute__(field)


def upd_many_to_many(field, request, instance, model):
    array = []
    if field in request.data:
        if request.data[field] != 'empty':
            for f in request.data[field]:
                array.append(model.objects.get(id=f['id']))
    elif instance:
        array = instance.__getattribute__(field).all()
    return array