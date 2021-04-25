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
from dictionaries.models import User
from . import views
from django.urls import include, path
from rest_framework.routers import SimpleRouter

router = SimpleRouter(trailing_slash=True)
router.register("notifies", views.NotifiesViewSet, basename=User)
router.register("credit_organizations", views.CreditOrganizationsViewSet, basename=User)
router.register("contrib_info", views.ContributionsInformationViewSet, basename=User)
router.register("contrib_info_mistake", views.ContributionsInformationMistakeViewSet, basename=User)
router.register('dashboard', views.DashboardViewSet, basename=User)
urlpatterns = [

]
urlpatterns += router.urls