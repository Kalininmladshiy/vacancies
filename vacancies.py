import requests
import os
from statistics import mean
from terminaltables import AsciiTable
from dotenv import load_dotenv


def predict_rub_salary_hh(vacancy):
    if vacancy['currency'] != 'RUR':
        return None
    elif vacancy['from'] and vacancy['to']:
        return int(mean([vacancy['from'], vacancy['to']]))
    elif not vacancy['from']:
        return int(vacancy['to'] * 0.8)
    elif not vacancy['to']:
        return int(vacancy['from'] * 1.2)


def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] != 'rub':
        return None
    elif vacancy['payment_from'] and vacancy['payment_to']:
        return int(mean([vacancy['payment_from'], vacancy['payment_to']]))
    elif not vacancy['payment_from']:
        return int(vacancy['payment_to'] * 0.8)
    elif not vacancy['payment_to']:
        return int(vacancy['payment_from'] * 1.2)


def get_beautiful_table(table_data, big_title):
    table = [
        [
            'Язык программирования',
            'Вакансий найдено',
            'Вакансий обработано',
            'Средняя зарплата',
            ],
     ]
    values = []
    for language, statistics in table_data.items():
        values.append(language)
        for title, value in statistics.items():
            values.append(str(value))
        table.append(values)
        values = []
    table = AsciiTable(table, big_title)
    return table.table


def get_avg_salary_hh(languages):
    url_hh = 'https://api.hh.ru/vacancies'
    headers_hh = {
        'User-Agent': 'HH-User-Agent',
        }
    avg_language_salary = {}
    vacancy_id = '1.221'
    moscow_id = '1'
    vacancies_for_a_period_days = '30'
    for language in languages:
        salaries = []
        page = 0
        pages_number = 1
        while page < pages_number:
            payload = {
                'specialization': vacancy_id,
                'area': moscow_id,
                'period': vacancies_for_a_period_days,
                'text': language,
                'only_with_salary': 'true',
                'currency': 'RUR',
                'page': page
                }
            response = requests.get(url_hh, headers=headers_hh, params=payload)
            response.raise_for_status()
            vacancies = response.json()['items']
            for vacancy in vacancies:
                predict_salary = predict_rub_salary_hh(vacancy['salary'])
                if predict_salary:
                    salaries.append(predict_salary)
            pages_number = response.json()['pages']
            page += 1
        avg_language_salary[language] = {
            "vacancies_found": response.json()['found'],
            "vacancies_processed": len(salaries),
            "average_salary": int(mean(salaries)),
        }
    return avg_language_salary


def get_avg_salary_sj(languages, secret_key):
    url_sj = 'https://api.superjob.ru/2.0/vacancies/'
    headers_sj = {
        'X-Api-App-Id': secret_key,
        }
    avg_language_salary = {}
    vacancy_id = 48
    moscow_id = 4
    vacancies_for_a_period_days = 7
    count_of_vacancies_per_page = 100
    for language in languages:
        salaries = []
        vacancies_found = 0
        page = 0
        pages_number = 2
        while page < pages_number:
            payload = {
                'catalogues': vacancy_id,
                'town': moscow_id,
                'period': vacancies_for_a_period_days,
                'keyword': language,
                'count': count_of_vacancies_per_page,
                'page': page
                }
            response = requests.get(url_sj, headers=headers_sj, params=payload)
            response.raise_for_status()
            vacancies = response.json()['objects']
            for vacancy_sj in vacancies:
                predict_salary = predict_rub_salary_sj(vacancy_sj)
                if predict_salary:
                    salaries.append(predict_salary)
            vacancies_found += len(vacancies)
            page += 1
        avg_language_salary[language] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": len(salaries),
            "average_salary": int(mean(salaries)),
        }
    return avg_language_salary


if __name__ == '__main__':
    load_dotenv()
    secret_key = os.environ['SJ_API_KEY']
    languages = [
        'JavaScript',
        'Java',
        'Python',
        'Ruby',
        'PHP',
        'C++',
        'C#',
        'C',
        'Go',
     ]
    print(get_beautiful_table(
        get_avg_salary_hh(languages),
        'HeadHunter Moscow',
     )
          )
    print(get_beautiful_table(
        get_avg_salary_sj(languages, secret_key),
        'SuperJob Moscow'
     )
          )
