from django.contrib.auth.models import Group, Permission

from capital_repair.models import ContributionsInformationMistake, ContributionsInformation, Notify, Status
from dictionaries import models
from mixer.backend.django import mixer

from dictionaries.models import User, Address, House


def populate_db():
    admin_group = mixer.blend(Group, name='Администраторы')
    admin_group.permissions.set(Permission.objects.all())
    uk_group = mixer.blend(Group, name='Управляющие организации')
    uk_group.permissions.set(
        [Permission.objects.get(codename='view_notify'),
         Permission.objects.get(codename='change_notify'),
         Permission.objects.get(codename='add_notify'),
         Permission.objects.get(codename='view_contributionsinformation'),
         Permission.objects.get(codename='change_contributionsinformation'),
         Permission.objects.get(codename='add_contributionsinformation')
         ])
    admin = mixer.blend(User, groups=[admin_group], username='admin', organization=mixer.RANDOM, is_staff=True)
    admin.set_password('123')
    admin.save()

    uk = mixer.blend(User, groups=[uk_group], username='uk',organization=mixer.blend(models.Organization), is_staff=False)
    uk.set_password('123')
    uk.save()

    mixer.cycle(5).blend(models.OrganizationType,
                         text=mixer.FAKE,
                         )
    mixer.cycle(25).blend(models.Organization,
                          name=mixer.FAKE,
                          inn=mixer.FAKE,
                          ogrn=mixer.FAKE,
                          type=mixer.SELECT
                          )

    n1 = mixer.blend(Status, id=1, text='Редактирование')
    n2 = mixer.blend(Status, id=2, text='Согласование')
    n3 = mixer.blend(Status, id=3, text='Согласовно')
    mistake1 = mixer.blend(ContributionsInformationMistake, text='Ошибка 1')
    mistake2 = mixer.blend(ContributionsInformationMistake, text='Ошибка 2')
    mistake3 = mixer.blend(ContributionsInformationMistake, text='Ошибка 3')
    n1 = mixer.blend(Notify, organization=mixer.SELECT)
    n2 = mixer.blend(Notify, organization=mixer.SELECT)
    n3 = mixer.blend(Notify, organization=mixer.SELECT)
    c1 = mixer.blend(ContributionsInformation, notify=n1, mistakes=[mistake1, mistake2], comment='c1')
    c2 = mixer.blend(ContributionsInformation, notify=n2, mistakes=[mistake1, mistake2], comment='c2')
    c3 = mixer.blend(ContributionsInformation, notify=n3, mistakes=[mistake3], comment='c3')
    mixer.cycle(100).blend(Notify, organization=mixer.SELECT)
    mixer.cycle(25).blend(Notify, organization=uk.organization)

    mixer.cycle(25).blend(Address)
    mixer.cycle(25).blend(House, address=mixer.SELECT)