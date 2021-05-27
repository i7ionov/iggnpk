"""far URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from . import views
from django.urls import include, path
from rest_framework.routers import SimpleRouter

from rest_framework.routers import SimpleRouter

from .models import User

router = SimpleRouter(trailing_slash=True)
router.register("organizations", views.OrganizationViewSet, basename=User)
router.register("organization_types", views.OrganizationTypeViewSet, basename=User)
router.register("addresses", views.AddressViewSet, basename=User)
router.register("houses", views.HouseViewSet, basename=User)
router.register("users", views.UserViewSet, basename=User)
router.register("groups", views.GroupViewSet, basename=User)
router.register("files", views.FileViewSet, basename=User)

urlpatterns = [
    path('files/create/', views.FileViewSet.as_view({'post': 'upload'})),
    path('send_message/', views.send_message),
    path('users/me/', views.me),
    path('users/register/', views.register),
    path('users/org_users_count/', views.org_users_count),
    path('users/is_email_already_used/', views.is_email_already_used),
    path('users/is_username_already_used/', views.is_username_already_used),
]
urlpatterns += router.urls
