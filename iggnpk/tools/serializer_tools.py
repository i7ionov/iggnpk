def upd_foreign_key(field, data, instance, model):
    if field in data:
        if instance.__getattribute__(field) is not None and data[field]['id'] == instance.__getattribute__(field).id:
            return instance.__getattribute__(field)
        return model.objects.get(id=data[field]['id'])
    else:
        return instance.__getattribute__(field)
