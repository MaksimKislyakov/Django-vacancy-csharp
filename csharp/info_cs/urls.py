from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.main),
    path('general_stat', views.general_stat),
    path('demand_stat', views.demand_stat),
    path('area_name_stat', views.area_name_stat),
    path('skills_top_stat', views.skills_top_stat),
]
