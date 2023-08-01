import os
import requests
from itertools import count
from terminaltables import AsciiTable
from dotenv import load_dotenv


HH_TITLE = "HeadHunter Moscow"
SJ_TITLE = "SuperJob Moscow"


def predict_rub_salary(salary_from=None, salary_to=None):
    if salary_from and salary_to:
        expected_salary = int((salary_to + salary_from) / 2)
    elif salary_to:
        expected_salary = int(salary_to * 1.2)
    elif salary_from:
        expected_salary = int(salary_from * 0.8)
    else:
        expected_salary = None
    return expected_salary


def get_vacancies_sj(key, language="Python", page=0):
    period_in_days = 30
    catalogue_count = 48
    url = "https://api.superjob.ru/2.0/vacancies/"
    headers = {"X-Api-App-Id": key}

    params = {
        "town": "Moscow",
        "period": period_in_days,
        "catalogues": catalogue_count,
        "keyword": language,
        "page": page
    }

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def get_statistic_vacancies_sj(sj_token):
    vacancies_by_language = {}
    languages = [
        "Python",
        "Java",
        "Javascript",
        "Ruby",
        "PHP",
        "C++",
        "C#",
        "C",
        "Go",
        "Shell"
    ]
    for language in languages:
        vacancies_processed = 0
        salary_by_vacancy = []
        for page in count(0, 1):
            vacancies = get_vacancies_sj(sj_token, language, page=page)
            if not vacancies['objects']:
                break
            for vacancy in vacancies['objects']:
                predicted_salary = predict_rub_salary(vacancy["payment_from"],
                                                 vacancy["payment_to"])
                if predicted_salary:
                    vacancies_processed += 1
                    salary_by_vacancy.append(predicted_salary)
        total_vacancies = vacancies['total']
        average_salary = None
        if salary_by_vacancy:
            average_salary = int(
                sum(salary_by_vacancy) / len(salary_by_vacancy))

        vacancies_by_language[language] = {
            'vacancies_found': total_vacancies,
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary
        }

    return vacancies_by_language


def get_vacancies_hh(language, page=0):
    area = 1
    url = 'https://api.hh.ru/vacancies'
    params = {'text': language, 'area': area, 'page': page}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def get_statistic_vacancies_hh():
    vacancies_by_language = {}
    languages = [
        "Python",
        "Java",
        "Javascript",
        "Ruby",
        "PHP",
        "C++",
        "C#",
        "C",
        "Go",
        "Shell"
    ]
    for language in languages:
        vacancies_processed = 0
        salary_by_vacancy = []
        for page in count(0):
            vacancies = get_vacancies_hh(language, page=page)
            if page >= vacancies["pages"] - 1:
                break
            for vacancy in vacancies['items']:
                salary = vacancy.get('salary')
                if salary and salary['currency'] == 'RUR':
                    predicted_salary = predict_rub_salary(
                        vacancy['salary'].get('from'),
                        vacancy['salary'].get('to'))
                    if predicted_salary:
                        vacancies_processed += 1
                        salary_by_vacancy.append(predicted_salary)
        total_vacancies = vacancies['found']
        average_salary = None
        if salary_by_vacancy:
            average_salary = int(
                sum(salary_by_vacancy) / len(salary_by_vacancy))

        vacancies_by_language[language] = {
            'vacancies_found': total_vacancies,
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary
        }

    return vacancies_by_language


def create_table(title, statistics):
    job_vacancy_table = [[
        "Язык программирования",
        "Вакансий найдено",
        "Вакансий обработано",
        "Средняя зарплата"
    ]]
    for language, vacancies in statistics.items():
        job_vacancy_table.append([
            language, vacancies["vacancies_found"],
            vacancies["vacancies_processed"], vacancies["average_salary"]
        ])
    table = AsciiTable(job_vacancy_table, title)
    return table.table


def main():
    load_dotenv()
    sj_token = os.environ['SJ_TOKEN']
    hh_table = create_table(HH_TITLE, get_statistic_vacancies_hh())
    sj_table = create_table(SJ_TITLE, get_statistic_vacancies_sj(sj_token))
    print(f"{sj_table}\n{hh_table}")


if __name__ == "__main__":
    main()
