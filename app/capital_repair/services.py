from datetime import datetime
from capital_repair.models import Status, CreditOrganization, Notify, ContributionsInformation, \
    ContributionsInformationMistake
from capital_repair.serializers import NotifySerializer, ContributionsInformationSerializer
from dictionaries.models import House, Organization, File
from tools.service import upd_foreign_key, ServiceException, upd_many_to_many


class ContributionsInformationService:
    private_fields = ['comment2']

    def create(self, data, user):
        exclude_fields = []
        if not user.is_staff:
            exclude_fields.extend(self.private_fields)
        serializer = ContributionsInformationSerializer(data=data, exclude=exclude_fields)
        serializer.is_valid()
        if serializer.is_valid():
            if data['status']['id'] > 2:
                raise ServiceException('Неправильный статус')
            status = Status.objects.get(id=data['status']['id'])
            notify = self._get_notify(data, None, user)
            files = upd_many_to_many('files', data, None, File)
            mistakes = self._get_mistakes(data, None, user)
            serializer.save(date=datetime.today().date(), status=status, files=files, notify=notify, last_notify=notify,
                            mistakes=mistakes)
            return serializer.data
        else:
            raise ServiceException(serializer.errors)

    def update(self, instance, data, user):
        exclude_fields = []
        data = data
        if not user.is_staff:
            if data['status']['id'] > 2:
                raise ServiceException('Неправильный статус')
            if instance.status.id > 2:
                raise ServiceException('Вы не можете редактировать эту запись')
            exclude_fields.append('comment2')

        serializer = ContributionsInformationSerializer(instance=instance, data=data, partial=True,
                                                        exclude=exclude_fields)
        serializer.is_valid()
        if serializer.is_valid():
            if 'status' in data and 'id' in data['status']:
                if instance.status is not None and data['status']['id'] == instance.status.id:
                    status = instance.status
                else:
                    status = Status.objects.get(id=data['status']['id'])
            else:
                status = instance.status
            if user.is_staff and 'date' in data:
                date = data['date']
            else:
                date = instance.date
            notify = self._get_notify(data, instance, user)
            files = upd_many_to_many('files', data, instance, File)
            mistakes = self._get_mistakes(data, instance, user)
            serializer.save(files=files, status=status, notify=notify, last_notify=notify, mistakes=mistakes, date=date)
            return serializer.data
        else:
            raise ServiceException(serializer.errors)

    def _get_mistakes(self, data, instance, user):
        """Возвращает массив ошибок для установки, если у пользователя есть на это права"""
        if user.is_staff:
            mistakes = upd_many_to_many('mistakes', data, instance, ContributionsInformationMistake)
        else:
            if instance:
                mistakes = instance.mistakes.all()
            else:
                mistakes = []
        return mistakes

    def _set_old_last_notify_to_none(self, notify):
        """Удаляет привязку к последней информации по взносам для уведомления
        для возможности привязки новой информации"""
        try:
            last_contrib = notify.last_contrib
            last_contrib.last_notify = None
            last_contrib.save()
        except ContributionsInformation.DoesNotExist:
            pass

    def _get_notify(self, data, instance, user):
        """Возвращает уведомление для записи"""
        notify = upd_foreign_key('notify', data, instance, Notify)
        self._set_old_last_notify_to_none(notify)
        if notify.organization.id != user.organization.id and not user.is_staff:
            raise ServiceException(
                'Организация, указанная в уведомлениии, не соответствует организации пользователя')
        return notify


class NotifyService:
    private_fields = ['comment2', 'date_of_exclusion', 'account_closing_date', 'ground_for_exclusion',
                      'source_of_information']

    def create(self, data, user):
        exclude_fields = []
        if not user.is_staff:
            exclude_fields.extend(self.private_fields)
        serializer = NotifySerializer(data=data, exclude=exclude_fields)
        serializer.is_valid()
        if serializer.is_valid():
            if data['status']['id'] > 2:
                raise ServiceException('Неправильный статус')
            status = Status.objects.get(id=data['status']['id'])
            bank = CreditOrganization.objects.get(id=data['bank']['id'])
            house, created = House.objects.get_or_create(address_id=data['house']['address']['id'],
                                                         number=str(data['house']['number']).strip().lower())
            if user.is_staff:
                org = Organization.objects.get(id=data['organization']['id'])
            else:
                org = user.organization
            files = upd_many_to_many('files', data, None, File)

            serializer.save(organization=org, date=datetime.today().date(), status=status,
                            bank=bank, files=files, house=house)
            return serializer.data
        else:
            raise ServiceException(serializer.errors)

    def update(self, instance, data, user):
        exclude_fields = []
        if not user.is_staff:
            if instance.status.id > 2:
                raise ServiceException('Вы не можете редактировать эту запись')
            if data['status']['id'] > 2:
                raise ServiceException('Неправильный статус')
            exclude_fields.extend(self.private_fields)

        serializer = NotifySerializer(instance=instance, data=data, partial=True, exclude=exclude_fields)
        if serializer.is_valid():
            if user.is_staff:
                org = upd_foreign_key('organization', data, instance, Organization)
            else:
                org = instance.organization
            if user.is_staff and 'date' in data:
                date = data['date']
            else:
                date = instance.date
            bank = upd_foreign_key('bank', data, instance, CreditOrganization)
            house = House.objects.get_or_create_new('house', data, instance)
            if 'status' in data and 'id' in data['status']:
                if instance.status is not None and data['status']['id'] == instance.status.id:
                    status = instance.status
                else:
                    status = Status.objects.get(id=data['status']['id'])
                    # присваиваем всем другим записям с этим домом статус Исключено
                    if status.text == 'Согласовано':
                        Notify.objects.filter(house_id=house.id, status_id=3).update(status_id=4,
                                                                                     date_of_exclusion=datetime.now())
                        house.organization = org
                        house.save()
            else:
                status = instance.status
            files = upd_many_to_many('files', data, instance, File)
            serializer.save(organization=org, bank=bank, house=house, files=files, status=status, date=date)
            return serializer.data
        else:
            raise ServiceException(serializer.errors)
