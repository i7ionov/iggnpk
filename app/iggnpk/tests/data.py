from capital_repair.models import ContributionsInformationMistake, ContributionsInformation
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
    mistake1 = ContributionsInformationMistake(text='Ошибка 1')
    mistake1.save()
    mistake2 = ContributionsInformationMistake(text='Ошибка 2')
    mistake2.save()
    mistake3 = ContributionsInformationMistake(text='Ошибка 3')
    mistake3.save()
    c1 = ContributionsInformation(received_contributions_total=3)
    c1.save()
    c1.mistakes.set([mistake1, mistake2])
    c2 = ContributionsInformation(received_contributions_total=2)
    c2.save()
    c2.mistakes.set([mistake1, mistake2])
