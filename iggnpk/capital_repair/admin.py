from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.CreditOrganization)
admin.site.register(models.Branch)
admin.site.register(models.Notify)
admin.site.register(models.Status)
admin.site.register(models.ContributionsInformationMistake)