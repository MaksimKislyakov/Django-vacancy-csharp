from django.shortcuts import render
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import re

PARSING_FILE = 'vacancies_2024.csv'
OUTPUT_FILE = 'scriptsJson/main.json'

# Курсы валют по месяцам
EXCHANGE_RATES = {
    '2010-08': {'BYR': 0.0101434, 'USD': 30.1869, 'EUR': 39.4694, 'KZT': 0.204352, 'UAH': 3.82316, 'AZN': 37.5646, 'KGS': 0.647093, 'UZS': 0.0188016},
}

# Ограничение на зарплату
MAX_SALARY = 10000000

# Функция для сохранения графиков в формате png картинок
def save_plot(data, title, xlabel, ylabel, filename):
    plt.figure(figsize=(10, 6))
    plt.plot(data.keys(), data.values(), marker='o')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig(filename)
    plt.close()

def process_data():
    chunksize = 100000
    csharp_vacancies = []

    for chunk in pd.read_csv(PARSING_FILE, usecols=['name', 'key_skills', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at'], chunksize=chunksize, encoding='utf-8'):
        # Преобразование столбца даты
        chunk['published_at'] = pd.to_datetime(chunk['published_at'], errors='coerce', utc=True)
        chunk['published_month'] = chunk['published_at'].dt.tz_localize(None).dt.to_period('M')

        # Фильтрация по C#
        csharp_jobs = chunk.loc[chunk['name'].str.contains(r'C#', case=False, na=False)]

        # Преобразование зарплаты в рубли
        def convert_salary(row):
            salary_from = row['salary_from'] or 0
            salary_to = row['salary_to'] or 0
            avg_salary = (salary_from + salary_to) / 2 if (salary_from + salary_to) > 0 else None

            if avg_salary and avg_salary <= MAX_SALARY:
                currency = row['salary_currency']
                month = str(row['published_month'])
                rate = EXCHANGE_RATES.get(month, {}).get(currency, 1)
                return avg_salary * rate

            return None

        csharp_jobs.loc[:, 'salary_rub'] = csharp_jobs.apply(convert_salary, axis=1)

        # Добавляем в общий список
        csharp_vacancies.append(csharp_jobs)

    # Объединение всех подходящих данных
    all_csharp_vacancies = pd.concat(csharp_vacancies)

    # Общий подсчет вакансий с зарплатой в рублях
    total_vacancies_rub = all_csharp_vacancies['salary_rub'].notna().sum()

    # Вычисление 1% от общего числа вакансий
    min_vacancies_for_city = total_vacancies_rub // 100

    # Аналитика
    stats = {}

    # Динамика зарплат по годам
    salary_trend = all_csharp_vacancies.groupby(all_csharp_vacancies['published_month'].dt.year)['salary_rub'].mean().to_dict()
    stats['salary_trend'] = salary_trend
    save_plot(salary_trend, 'Динамика уровня зарплат по годам', 'Год', 'Средняя зарплата (руб.)', 'salary_trend.png')

    # Количество вакансий по годам
    vacancy_trend = all_csharp_vacancies.groupby(all_csharp_vacancies['published_month'].dt.year).size().to_dict()
    stats['vacancy_trend'] = vacancy_trend
    save_plot(vacancy_trend, 'Динамика количества вакансий по годам', 'Год', 'Количество вакансий', 'vacancy_trend.png')

    # Уровень зарплат по городам (с фильтрацией по 1% от общего числа вакансий)
    city_vacancies = all_csharp_vacancies.groupby('area_name').size()
    valid_cities = city_vacancies[city_vacancies >= min_vacancies_for_city].index
    salary_by_city = all_csharp_vacancies[all_csharp_vacancies['area_name'].isin(valid_cities)].groupby('area_name')['salary_rub'].mean().sort_values(ascending=False).to_dict()
    stats['salary_by_city'] = salary_by_city
    save_plot(salary_by_city, 'Уровень зарплат по городам', 'Город', 'Средняя зарплата (руб.)', 'salary_by_city.png')

    # Доля вакансий по городам (с фильтрацией по 1% от общего числа вакансий)
    vacancy_share_by_city = (all_csharp_vacancies[all_csharp_vacancies['area_name'].isin(valid_cities)]['area_name'].value_counts(normalize=True) * 100).sort_values(ascending=False).to_dict()
    stats['vacancy_share_by_city'] = vacancy_share_by_city
    save_plot(vacancy_share_by_city, 'Доля вакансий по городам', 'Город', 'Доля вакансий (%)', 'vacancy_share_by_city.png')

    # Топ-20 навыков по годам
    def extract_skills(key_skills):
        if pd.isna(key_skills):
            return []
        # Разделение навыков по запятой и новой строке
        return [skill.strip() for skill in re.split(r',|\n', key_skills) if skill.strip()]

    all_csharp_vacancies['skills'] = all_csharp_vacancies['key_skills'].apply(extract_skills)
    skill_trends = {}
    for year, group in all_csharp_vacancies.groupby(all_csharp_vacancies['published_month'].dt.year):
        all_skills = group['skills'].explode()
        skill_trends[year] = all_skills.value_counts().head(20).to_dict()

    stats['top_skills'] = skill_trends

    # Сохранение в JSON
    with open('main.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)

# process_data()

# Представление Django
def main(request):
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Составляем список с путями к изображениям графиков
    graphics_files = {
        'salary_trend': 'graphics/salary_trend.png',
        'vacancy_trend': 'graphics/vacancy_trend.png',
        'salary_by_city': 'graphics/salary_by_city.png',
        'vacancy_share_by_city': 'graphics/vacancy_share_by_city.png',
    }

    return render(request, 'main.html', {'data': data, 'graphics_files': graphics_files})

