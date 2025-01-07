from django.contrib import admin
from .models import Vacancy, Statistic

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ("title", "company_name", "area", "salary_from", "salary_to", "published_at")
    search_fields = ("title", "company_name", "area")
    list_filter = ("area", "published_at", "currency")

@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)