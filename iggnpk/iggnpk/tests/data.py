
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