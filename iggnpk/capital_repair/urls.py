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
    path('credit_organizations/', views.CreditOrganisationsViewSet.as_view({'get': 'list'})),
    path('credit_organizations/<int:pk>/', views.CreditOrganisationsViewSet.as_view({'get': 'retrieve'})),
    path('credit_organizations/search/', views.CreditOrganisationsViewSet.as_view({'get': 'search'})),

    path('branches/', views.BranchViewSet.as_view({'get': 'list'})),
    path('branches/<int:pk>/', views.BranchViewSet.as_view({'get': 'retrieve'})),
    path('branches/search/', views.BranchViewSet.as_view({'get': 'search'})),

    path('notifies/', views.NotifiesViewSet.as_view({'get': 'list'})),
    path('notifies/create/', views.NotifiesViewSet.as_view({'post': 'create'})),
    path('notifies/<int:pk>/', views.NotifiesViewSet.as_view({'get': 'retrieve'})),
    path('notifies/save/<int:pk>/', views.NotifiesViewSet.as_view({'post': 'update'})),
    path('notifies/search/', views.NotifiesViewSet.as_view({'get': 'search'})),

    path('contrib_info/', views.ContributionsInformationViewSet.as_view({'get': 'list'})),
    path('contrib_info/create/', views.ContributionsInformationViewSet.as_view({'post': 'create'})),
    path('contrib_info/<int:pk>/', views.ContributionsInformationViewSet.as_view({'get': 'retrieve'})),
    path('contrib_info/save/<int:pk>/', views.ContributionsInformationViewSet.as_view({'post': 'update'})),
    path('contrib_info/generate_act/<int:pk>/', views.ContributionsInformationViewSet.as_view({'get': 'generate_act'})),

    path('contrib_info_mistake/', views.ContributionsInformationMistakeViewSet.as_view({'get': 'list'})),
    path('contrib_info_mistake/<int:pk>/', views.ContributionsInformationMistakeViewSet.as_view({'get': 'retrieve'})),
    path('contrib_info_mistake/search/', views.ContributionsInformationMistakeViewSet.as_view({'get': 'search'})),

]
