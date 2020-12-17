from capital_repair.models import ContributionsInformationMistake, ContributionsInformation, Notify
from dictionaries import models
from mixer.backend.django import mixer


def create_organizations():
    mixer.cycle(5).blend(models.OrganizationType,
                         text=mixer.FAKE,
                         )
    mixer.cycle(25).blend(models.Organization,
                         name=mixer.FAKE,
                         inn=mixer.FAKE,
                         ogrn=mixer.FAKE,
                         type=mixer.SELECT
                         )


def create_conrib_infos():
    mistake1 = mixer.blend(ContributionsInformationMistake, text='Ошибка 1')
    mistake2 = mixer.blend(ContributionsInformationMistake, text='Ошибка 2')
    mistake3 = mixer.blend(ContributionsInformationMistake, text='Ошибка 3')
    n1 = mixer.blend(Notify)
    n2 = mixer.blend(Notify)
    n3 = mixer.blend(Notify)
    c1 = mixer.blend(ContributionsInformation, notify=n1, mistakes=[mistake1, mistake2], comment='c1')
    c2 = mixer.blend(ContributionsInformation, notify=n2, mistakes=[mistake1, mistake2], comment='c2')
    c3 = mixer.blend(ContributionsInformation, notify=n3, mistakes=[mistake3], comment='c3')
