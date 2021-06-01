from django.contrib.auth.models import Group
from django.core.mail import send_mail
from dictionaries.models import Address, OrganizationType, Organization, User
from dictionaries.serializers import HouseSerializer, OrganizationSerializer, AddressSerializer, UserSerializer
from dictionaries.address_normalizer import normalize_number, normalize_street, normalize_city
from tools.replace_quotes import replace_quotes
from tools.service import ServiceException, upd_foreign_key, upd_many_to_many


class HouseService:
    def create(self, data, user):
        serializer = HouseSerializer(data=data)
        serializer.is_valid()
        if serializer.is_valid():
            addr = Address.objects.get(id=data['address']['id'])
            serializer.save(address=addr, number=normalize_number(data['number']))
            return serializer.data
        else:
            raise ServiceException(serializer.errors)

    def update(self, instance, data, user):
        serializer = HouseSerializer(instance=instance, data=data, partial=True)
        if serializer.is_valid():
            addr = upd_foreign_key('address', data, instance, Address)
            serializer.save(address=addr, number=normalize_number(data['number']))
            return serializer.data
        else:
            raise ServiceException(serializer.errors)


class OrganizationService:
    def create(self, data, user):
        serializer = OrganizationSerializer(data=data)
        if serializer.is_valid():
            org_type = OrganizationType.objects.get(id=data['type']['id'])
            serializer.save(type=org_type, name=replace_quotes(data['name']))
            return serializer.data
        else:
            raise ServiceException(serializer.errors)

    def update(self, instance, data, user):
        serializer = OrganizationSerializer(instance=instance, data=data, partial=True)
        if serializer.is_valid():
            org_type = upd_foreign_key('type', data, instance, OrganizationType)
            serializer.save(type=org_type)
            return serializer.data
        else:
            raise ServiceException(serializer.errors)


class AddressService:
    def create(self, data, user):
        serializer = AddressSerializer(data=data)
        serializer.is_valid()
        if serializer.is_valid():
            serializer.save(street=normalize_street(data['street']),
                            city=normalize_city(data['city']))
            return serializer.data
        else:
            raise ServiceException(serializer.errors)

    def update(self, instance, data, user):
        serializer = AddressSerializer(instance=instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(street=normalize_street(data['street']),
                            city=normalize_city(data['city']))
            return serializer.data
        else:
            raise ServiceException(serializer.errors)


class UserService:
    def register(self, data):
        """Регистрация пользователем"""
        item = UserSerializer(data=data)
        if item.is_valid():
            if data['password'] != data['re_password']:
                raise ServiceException('Пароли не совпадают')
            if 'organization' not in data:
                raise ServiceException('Не указана организация')
            if 'name' not in data['organization']:
                raise ServiceException('Не указано наименование организации')
            if 'inn' not in data['organization']:
                raise ServiceException('Не указан ИНН организации')
            if 'ogrn' not in data['organization']:
                raise ServiceException('Не указан ОГРН организации')
            if 'type' not in data['organization'] or 'id' not in data['organization']['type']:
                raise ServiceException('Не указан тип организации')
            org, created = Organization.objects.get_or_create(inn=data['organization']['inn'])
            if created:
                org.name = data['organization']['name']
                org.ogrn = data['organization']['ogrn']
                org.type = OrganizationType.objects.get(id=data['organization']['type']['id'])
                org.save()
            User.objects.create_user(username=data['username'], organization=org,
                                     password=data['password'], email=data['email']) \
                .groups.add(Group.objects.get(name='Управляющие организации'))
            return item.data
        else:
            raise ServiceException(item.errors)

    def create(self, data, user):
        """Создание пользователя администратором"""
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            if 'organization' not in data or 'id' not in data['organization']:
                raise ServiceException('Не выбрана организация')
            if 'password' not in data or 're_password' not in data:
                raise ServiceException('Не указан пароль')
            if data['password'] != data['re_password']:
                raise ServiceException('Пароли не совпадают')
            org = Organization.objects.get(id=data['organization']['id'])
            groups = upd_many_to_many('groups', data, None, Group)
            is_staff = Group.objects.get(name='Администраторы') in groups
            if 'is_active' not in data:
                is_active = False
            else:
                is_active = data['is_active']
            if len(groups) == 0:
                groups.append(Group.objects.get(name='Управляющие организации'))
            serializer.save(organization=org, groups=groups, is_active=is_active, is_staff=is_staff)
            user = User.objects.get(id=serializer.instance.id)
            user.set_password(data['password'])
            user.save()
            return serializer.data
        else:
            raise ServiceException(serializer.errors)

    def update(self, instance, data, user):
        if data['id'] != 1 and user.has_perm('dictionaries.change_user'):
            serializer = UserSerializer(instance=instance, data=data, partial=True)
            if serializer.is_valid():
                if 'password' in data:
                    if data['password'] != data['re_password']:
                        raise ServiceException('Пароли не совпадают')
                    instance.set_password(data['password'])
                org = upd_foreign_key('organization', data, instance, Organization)
                groups = upd_many_to_many('groups', data, None, Group)
                is_staff = Group.objects.get(name='Администраторы') in groups
                serializer.save(organization=org, groups=groups, is_staff=is_staff)
                self._send_activation_mail(data, serializer)
                return serializer.data
            else:
                raise ServiceException(serializer.errors)
        raise ServiceException('У вас нет соответствующих прав')

    def _send_activation_mail(self, data, serializer):
        """Отправка уведомления об активации/деактивации учетной записи"""
        if 'sendmail' in data and data['sendmail']:
            if serializer.data['is_active']:
                message = 'активировна'
            else:
                message = 'отключена'
            send_mail(
                f'Учетная запись на портале iggnpk.ru {message}',
                f'Учетная запись на портале iggnpk.ru {message}',
                'noreply@iggnpk.ru',
                [serializer.data['email']],
                fail_silently=False,
            )


