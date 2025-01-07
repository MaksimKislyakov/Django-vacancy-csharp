from django.shortcuts import render
import json
import requests
from datetime import datetime, timedelta
import re

#json для профессии
OUTPUT_FILE_NEED_VAC = 'scriptsJson/csharp_stat.json'

#json для общей статистики
OUTPUT_FILE_GENGERAL = 'scriptsJson/general.json'

HH_API_URL = "https://api.hh.ru/vacancies"
KEYWORDS = ['c#', 'c sharp', 'шарп', 'с#']

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

def fetch_vacancies():
    # Формирование запроса для API
    params = {
        'text': ' OR '.join(KEYWORDS),  # Поиск по ключевым словам
        'area': 1,  # Регион Россия
        'date_from': (datetime.utcnow() - timedelta(days=1)).isoformat(),  # Последние 24 часа
        'per_page': 10,
        'page': 0,
        'only_with_salary': False
    }
    response = requests.get(HH_API_URL, params=params)
    response.raise_for_status()  # Проверка статуса ответа
    vacancies = response.json().get('items', [])

    # Дополнительная обработка вакансий
    detailed_vacancies = []
    for vacancy in vacancies:
        details = requests.get(vacancy['url']).json()  # Доп. GET-запрос
        description = re.sub(r'<.*?>', '', details.get('description', 'Нет описания'))
        detailed_vacancies.append({
            'name': details.get('name', 'Не указано'),
            'description': description,
            'skills': ', '.join(skill['name'] for skill in details.get('key_skills', [])),
            'company': details.get('employer', {}).get('name', 'Не указано'),
            'salary': format_salary(details.get('salary')),
            'area': details.get('area', {}).get('name', 'Не указано'),
            'published_at': details.get('published_at', 'Не указано')
        })
    
    detailed_vacancies.sort(
        key=lambda x: datetime.fromisoformat(x['published_at']),
        reverse=True 
    )

    return detailed_vacancies

def format_salary(salary):
    if not salary:
        return "Не указано"
    if salary['currency'] != 'RUR':
        return "Не в рублях"
    return f"{salary['from'] or ''} - {salary['to'] or ''} {salary['currency']}"

def latest_vacancies(request):
    vacancies = fetch_vacancies()
    return render(request, 'latest_vacancies.html', {'vacancies': vacancies})