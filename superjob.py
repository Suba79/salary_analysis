
import os

import requests
from dotenv import load_dotenv


def predict_rub_salary_for_superjob(vacancy):
    if vacancy.get("currency") != "rub" or vacancy.get("agreement"):
        return None

    salary_from = vacancy.get("payment_from")
    salary_to = vacancy.get("payment_to")

    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    if salary_from:
        return salary_from * 1.2
    if salary_to:
        return salary_to * 0.8

    return None


def get_superjob_statistics(languages):
    load_dotenv()
    api_key = os.getenv("SUPERJOB_API_KEY")

    if not api_key:
        raise ValueError("Не найден SUPERJOB_API_KEY в .env")

    headers = {"X-Api-App-Id": api_key}
    url = "https://api.superjob.ru/2.0/vacancies/"
    statistics = {}

    for language in languages:
        total_salary = 0
        vacancies_processed = 0
        page = 0
        vacancies_found = 0

        while page < 5:
            params = {
                "keyword": language,
                "town": 4,
                "catalogues": 48,
                "count": 100,
                "page": page,
            }

            response = requests.get(
                url, headers=headers, params=params, timeout=30
            )
            response.raise_for_status()

            data = response.json()

            if page == 0:
                vacancies_found = data["total"]

            for vacancy in data["objects"]:
                salary = predict_rub_salary_for_superjob(vacancy)

                if salary is not None:
                    total_salary += salary
                    vacancies_processed += 1

            if not data["more"]:
                break

            page += 1

        average_salary = (
            int(total_salary / vacancies_processed)
            if vacancies_processed else 0
        )

        statistics[language] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": vacancies_processed,
            "average_salary": average_salary,
        }

    return statistics
