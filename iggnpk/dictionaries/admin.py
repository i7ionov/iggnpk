from django.contrib import admin
from .models import User, House, Address, Organization, OrganizationType

admin.site.register(User)
admin.site.register(House)
admin.site.register(Address)
admin.site.register(Organization)
admin.site.register(OrganizationType)