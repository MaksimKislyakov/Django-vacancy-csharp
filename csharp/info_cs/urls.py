from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.main),
    path('demand_statistics/', views.demand_statistics),
]
