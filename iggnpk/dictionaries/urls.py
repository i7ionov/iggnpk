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


urlpatterns = [
    path('organizations/', views.OrganizationViewSet.as_view({'get': 'list'})),
    path('organizations/<int:pk>/', views.OrganizationViewSet.as_view({'get': 'retrieve'})),
    path('organizations/search/', views.OrganizationViewSet.as_view({'get': 'search'})),
    path('organizations/types/', views.OrganizationViewSet.as_view({'get': 'types'})),
    path('org_users_count/', views.org_users_count),
    path('is_email_already_used/', views.is_email_already_used),
    path('houses/', views.HouseViewSet.as_view({'get': 'list'})),
    path('houses/<int:pk>/', views.HouseViewSet.as_view({'get': 'retrieve'})),
    path('addresses/', views.AddressViewSet.as_view({'get': 'list'})),
    path('addresses/<int:pk>/', views.AddressViewSet.as_view({'get': 'retrieve'})),
    path('addresses/search/', views.AddressViewSet.as_view({'get': 'search'})),
    path('users/me/', views.UserViewSet.as_view({'get': 'me'})),
    path('users/create/', views.UserViewSet.as_view({'post': 'create'})),
    path('files/create/', views.FileViewSet.as_view({'post': 'upload'})),

]
