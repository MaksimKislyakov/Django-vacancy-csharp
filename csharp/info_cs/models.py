from django.db import models

class Vacancy(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    salary = models.PositiveIntegerField()
    experience = models.PositiveIntegerField()
    company_name = models.CharField(max_length=200)