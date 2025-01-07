from django.db import models

class Vacancy(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название вакансии")
    description = models.TextField(verbose_name="Описание")
    salary_from = models.PositiveIntegerField(null=True, blank=True, verbose_name="Зарплата от")
    salary_to = models.PositiveIntegerField(null=True, blank=True, verbose_name="Зарплата до")
    currency = models.CharField(max_length=10, default="RUR", verbose_name="Валюта")
    experience = models.CharField(max_length=100, verbose_name="Опыт", blank=True)
    company_name = models.CharField(max_length=200, verbose_name="Название компании")
    skills = models.TextField(blank=True, verbose_name="Навыки")
    area = models.CharField(max_length=100, verbose_name="Регион")
    published_at = models.DateTimeField(verbose_name="Дата публикации")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"

class Statistic(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(verbose_name="Описание", blank=True)
    file = models.FileField(upload_to='statistics/', blank=True, verbose_name="График (файл)")
    content = models.TextField(blank=True, verbose_name="HTML-содержание")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Статистика"
        verbose_name_plural = "Статистика"