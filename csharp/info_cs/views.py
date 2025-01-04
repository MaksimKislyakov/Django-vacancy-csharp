from django.shortcuts import render
import json


#json для профессии
OUTPUT_FILE_NEED_VAC = 'scriptsJson/csharp_stat.json'

#json для общей статистики
OUTPUT_FILE_GENGERAL = 'scriptsJson/general.json'

def main(request):
    return render(request, 'main.html', {})

def general_stat(request):
    with open(OUTPUT_FILE_GENGERAL, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return render(request, 'general_stat.html', {'data': data})

def demand_stat(request):
    with open(OUTPUT_FILE_NEED_VAC, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return render(request, 'demand_stat.html', {'data': data})

def area_name_stat(request):
    with open(OUTPUT_FILE_NEED_VAC, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return render(request, 'area_name_stat.html', {'data': data})

def skills_top_stat(request):
    with open(OUTPUT_FILE_NEED_VAC, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return render(request, 'skills_top_stat.html', {'data': data})