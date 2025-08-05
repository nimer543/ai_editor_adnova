"""
URL configuration for ai_ideator_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from django.urls import path
from .views import about
from . import views

urlpatterns = [
    path('',about,name='about'),
    path('step1/',views.multi_step_form_view,{'step_number':1},name='step1'),
    path('step2/',views.multi_step_form_view,{'step_number':2},name='step2'),
    path('step3/',views.multi_step_form_view,{'step_number':3},name='step3'),
    path('results/', views.results_view, name='results'),
    path('loading/', views.loading,name='loading')


    
]
