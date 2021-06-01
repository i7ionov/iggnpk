import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.auth.base_user import BaseUserManager
from simple_history.models import HistoricalRecords


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Создает и сохраняет пользователя с введенным им email и паролем.
        """
        if not email:
            raise ValueError('email должен быть указан')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.is_active = False
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class OrganizationType(models.Model):
    text = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.text


class Organization(models.Model):
    inn = models.CharField(max_length=30, blank=True)
    ogrn = models.CharField(max_length=30, blank=True)
    name = models.CharField(max_length=100, blank=True)
    type = models.ForeignKey(OrganizationType, on_delete=models.SET_NULL, null=True, blank=True)
    # информация о смене название
    date_of_changind_name = models.DateField(blank=True, null=True)
    old_name = models.CharField(max_length=100, blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return f'{self.name}, ИНН {self.inn}'


class User(AbstractUser):
    name = models.CharField(max_length=100, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, verbose_name='Организация',
                                     blank=True)
    history = HistoricalRecords()
    REQUIRED_FIELDS = ['email', 'name']
    objects = UserManager()

    def permissions(self):
        if self.is_superuser:
            return Permission.objects.all()
        return self.user_permissions.all() | Permission.objects.filter(group__user=self)


class Address(models.Model):
    area = models.CharField(max_length=100, verbose_name='Район')
    place = models.CharField(max_length=100, verbose_name='Муниципальное образование')
    city = models.CharField(max_length=100, verbose_name='Населенный пункт')
    city_weight = models.IntegerField(default=100)
    street = models.CharField(max_length=100, verbose_name='Улица')

    def __str__(self):
        return f'{self.city}, {self.street}'

    class Meta:
        verbose_name = "Адрес"


def upload_path_handler(instance, filename):
    return "{inn}/{file}".format(inn=instance.owner.organization.inn, file=filename)


class File(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, to_field='id', on_delete=models.SET_NULL, null=True, blank=True)
    datafile = models.FileField(upload_to=upload_path_handler, null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name='Название файла')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        verbose_name = "Файл"


class HouseManager(models.Manager):
    def get_or_create_new(self, field, data, instance):
        if field in data:
            if 'address' in data[field]:
                addr_id = data[field]['address']['id']
            else:
                addr_id = instance.__getattribute__(field).address.id
            if 'number' in data[field]:
                number = data[field]['number']
            else:
                number = instance.__getattribute__(field).number
            result, created = House.objects.get_or_create(address_id=addr_id, number=str(number).strip().lower())
            return result
        else:
            return instance.__getattribute__(field)


class House(models.Model):
    number = models.CharField(max_length=100, verbose_name='Номер дома')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, verbose_name='Адрес')
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, verbose_name='Организация',
                                     blank=True)
    license_registry_organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True,
                                                      verbose_name='Организация, управляющая согласно реестру лицензий',
                                                      blank=True, related_name='license_registry_house')
    included_in_the_regional_program = models.BooleanField(null=True, blank=True)
    date_of_inclusion = models.DateField(
        verbose_name='Дата включения МКД в Региональную программу капитального ремонта', null=True, blank=True)
    year_of_building = models.IntegerField(verbose_name='Дата постройки', null=True, blank=True)
    number_of_apartments = models.IntegerField(null=True, blank=True, verbose_name='Количество квартир')
    total_area = models.FloatField(null=True, blank=True, verbose_name='Общая площадь')
    residential_premises_area = models.FloatField(null=True, blank=True, verbose_name='Общая площадь жилых помещений')
    nonresidential_premises_area = models.FloatField(null=True, blank=True,
                                                     verbose_name='Общая площадь нежилых помещений')

    history = HistoricalRecords()
    objects = HouseManager()

    def __str__(self):
        return f'{self.address}, {self.number}'

    class Meta:
        verbose_name = "Дом"
