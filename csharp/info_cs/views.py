from django.db.models import Avg, Count, F
from django.shortcuts import render, get_object_or_404
from .models import *

def main(request):
    return render(request, 'main.html', {'name': 'Максим'})

def demand_statistics(request):
    return render(request, 'demand_stat.html', {})
