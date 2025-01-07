import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import re
import requests
import pandas as pd
import xml.etree.ElementTree as ET

def get_all_currency():
    month = 1
    year = 2003
    all_currency = 'BYR,USD,EUR,KZT,UAH,AZN,KGS,UZS,GEL'.split(',')
    len_cur = len(all_currency)
    result = {}
    while True:
        if year == 2024 and month == 12:
            break
        month_str = str(month)
        if month < 10:
            month_str = '0' + month_str
        try:
          response = requests.get(f'https://cbr.ru/scripts/XML_daily.asp?date_req=01/{month_str}/{year}')
          result[f'{year}-{month_str}'] = {}
          root = ET.fromstring(response.content)
          for item in root.findall('Valute'):
              name = item.find('CharCode').text
              try:
                  index = all_currency.index(name) + 1
                  result[f'{year}-{month_str}'][name] = float(item.find('VunitRate').text.replace(',', '.'))
              except ValueError:
                  continue
        except Exception:
            continue
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1
    return result

# Получаем курсы валют из Центрального банка России
EXCHANGE_RATES = get_all_currency()

PARSING_FILE = 'vacancies_2024.csv'
#json для профессии
OUTPUT_FILE_NEED_VAC = 'scriptsJson/csharp_stat.json'

#json для общей статистики
OUTPUT_FILE_GENGERAL = 'scriptsJson/general.json'

# Ограничение на зарплату
MAX_SALARY = 10000000

KEYWORDS = ['c#', 'c sharp', 'шарп']

# Функция для сохранения графиков в формате png картинок

def save_plot(data, title, ylabel, xlabel, filename):
    plt.figure(figsize=(10, 6))
    if isinstance(data, dict):
        plt.barh(data.keys(), data.values(), color='skyblue')
    else:
        plt.plot(data.keys(), data.values(), marker='o', color='skyblue')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=0)
    plt.tight_layout(pad=2.0)
    plt.savefig(filename)
    plt.close()

def process_data_need_vac():
    chunksize = 100000
    all_vac = []

    for chunk in pd.read_csv(PARSING_FILE, usecols=['name', 'key_skills', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at'], chunksize=chunksize, encoding='utf-8'):
        # Преобразование столбца даты
        chunk['published_at'] = pd.to_datetime(chunk['published_at'], errors='coerce', utc=True)
        chunk['published_month'] = chunk['published_at'].dt.tz_localize(None).dt.to_period('M')

        # Фильтрация по C#
        pattern_csharp = r'|'.join([re.escape(keyword) for keyword in KEYWORDS])

        # Фильтрация строк
        csharp = chunk.loc[chunk['name'].str.contains(pattern_csharp, case=False, na=False)]

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

        csharp.loc[:, 'salary_rub'] = csharp.apply(convert_salary, axis=1)

        # Добавляем в общий список
        all_vac.append(csharp)

    # Объединение всех подходящих данных
    all_vac_concat = pd.concat(all_vac)

    # Общий подсчет вакансий с зарплатой в рублях
    total_vacancies_rub = all_vac_concat['salary_rub'].notna().sum()

    # Вычисление 1% от общего числа вакансий
    min_vacancies_for_city = total_vacancies_rub // 100

    # Аналитика
    stats = {}

    # Динамика зарплат по годам
    salary_trend = all_vac_concat.groupby(all_vac_concat['published_month'].dt.year)['salary_rub'].mean().to_dict()
    stats['salary_trend'] = salary_trend
    save_plot(salary_trend, 'Динамика уровня зарплат по годам', 'Год', 'Средняя зарплата (руб.)', 'salary_trend.png')

    # Количество вакансий по годам
    vacancy_trend = all_vac_concat.groupby(all_vac_concat['published_month'].dt.year).size().to_dict()
    stats['vacancy_trend'] = vacancy_trend
    save_plot(vacancy_trend, 'Динамика количества вакансий по годам', 'Год', 'Количество вакансий', 'vacancy_trend.png')

    # Уровень зарплат по городам (с фильтрацией по 1% от общего числа вакансий)
    city_vacancies = all_vac_concat.groupby('area_name').size()
    valid_cities = city_vacancies[city_vacancies >= min_vacancies_for_city].index
    salary_by_city = all_vac_concat[all_vac_concat['area_name'].isin(valid_cities)].groupby('area_name')['salary_rub'].mean().sort_values(ascending=False).to_dict()
    stats['salary_by_city'] = salary_by_city
    save_plot(salary_by_city, 'Уровень зарплат по городам', 'Город', 'Средняя зарплата (руб.)', 'salary_by_city.png')

    # Доля вакансий по городам (с фильтрацией по 1% от общего числа вакансий)
    vacancy_share_by_city = (all_vac_concat[all_vac_concat['area_name'].isin(valid_cities)]['area_name'].value_counts(normalize=True) * 100).sort_values(ascending=False).to_dict()
    stats['vacancy_share_by_city'] = vacancy_share_by_city
    save_plot(vacancy_share_by_city, 'Доля вакансий по городам', 'Город', 'Доля вакансий (%)', 'vacancy_share_by_city.png')

    # Топ-20 навыков по годам
    def extract_skills(key_skills):
        if pd.isna(key_skills):
            return []
        # Разделение навыков по запятой и новой строке
        return [skill.strip() for skill in re.split(r',|\n', key_skills) if skill.strip()]

    all_vac_concat['skills'] = all_vac_concat['key_skills'].apply(extract_skills)
    skill_trends = {}
    for year, group in all_vac_concat.groupby(all_vac_concat['published_month'].dt.year):
        all_skills = group['skills'].explode()
        skill_trends[year] = all_skills.value_counts().head(20).to_dict()
    
    stats['top_skills'] = skill_trends
    for year, skill in skill_trends.items():
        save_plot(skill, 'ТОП-20 навыков по годам', 'Навык', 'Количество навыков', f'skills_top_20_in_{year}.png')

    # Сохранение в JSON
    with open('main.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)


def process_all_vacancies():
    chunksize = 100000
    all_data = []

    for chunk in pd.read_csv(PARSING_FILE, chunksize=chunksize, encoding='utf-8',
                             usecols=['name', 'key_skills', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at']):
        chunk['published_at'] = pd.to_datetime(chunk['published_at'], errors='coerce', utc=True)
        chunk['published_month'] = chunk['published_at'].dt.tz_localize(None).dt.to_period('M')

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

        chunk['salary_rub'] = chunk.apply(convert_salary, axis=1)
        all_data.append(chunk)

    all_data = pd.concat(all_data)

    total_vacancies = all_data['salary_rub'].notna().sum()
    min_vacancies_for_city = total_vacancies // 100

    stats = {}

    # Динамика уровня зарплат по годам
    salary_trend = all_data.groupby(all_data['published_month'].dt.year)['salary_rub'].mean().to_dict()
    stats['salary_trend'] = salary_trend
    save_plot(salary_trend, 'Динамика уровня зарплат по годам', 'Год', 'Средняя зарплата (руб.)', 'salary_trend_g.png')

    # Динамика количества вакансий по годам
    vacancy_trend = all_data.groupby(all_data['published_month'].dt.year).size().to_dict()
    stats['vacancy_trend'] = vacancy_trend
    save_plot(vacancy_trend, 'Динамика количества вакансий по годам', 'Год', 'Количество вакансий', 'vacancy_trend_g.png')

    # Уровень зарплат по городам
    city_vacancies = all_data.groupby('area_name').size()
    valid_cities = city_vacancies[city_vacancies >= min_vacancies_for_city].index
    salary_by_city = all_data[all_data['area_name'].isin(valid_cities)].groupby('area_name')['salary_rub'].mean().sort_values(ascending=False).to_dict()
    stats['salary_by_city'] = salary_by_city
    save_plot(salary_by_city, 'Уровень зарплат по городам', 'Город', 'Средняя зарплата (руб.)', 'salary_by_city_g.png')

    # Доля вакансий по городам
    vacancy_share_by_city = (all_data[all_data['area_name'].isin(valid_cities)]['area_name']
                              .value_counts(normalize=True) * 100).sort_values(ascending=False).to_dict()
    stats['vacancy_share_by_city'] = vacancy_share_by_city
    save_plot(vacancy_share_by_city, 'Доля вакансий по городам', 'Город', 'Доля вакансий (%)', 'vacancy_share_by_city_g.png')

    # TТОП-20 навыков по годам
    def extract_skills(key_skills):
        if pd.isna(key_skills):
            return []
        return [skill.strip() for skill in re.split(r',|\n', key_skills) if skill.strip()]

    all_data['skills'] = all_data['key_skills'].apply(extract_skills)
    skill_trends = {}
    for year, group in all_data.groupby(all_data['published_month'].dt.year):
        all_skills = group['skills'].explode()
        skill_trends[year] = all_skills.value_counts().head(20).to_dict()

    stats['top_skills'] = skill_trends
    for year, skills in skill_trends.items():
        save_plot(skills, f'ТОП-20 навыков за {year}', 'Навык', 'Количество упоминаний', f'top_skills_{year}_g.png')

    # Сохранение в json файл
    with open('general.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)

process_data_need_vac()
process_all_vacancies()

