
import os

import requests
from dotenv import load_dotenv

from salary import predict_salary


SUPERJOB_MOSCOW_CITY_ID = 4
SUPERJOB_PROGRAMMING_CATEGORY_ID = 48
SUPERJOB_PAGE_SIZE = 100
SUPERJOB_MAX_PAGES = 5
REQUEST_TIMEOUT_SECONDS = 30


def predict_rub_salary_for_superjob(vacancy):
    if vacancy.get("currency") != "rub" or vacancy.get("agreement"):
        return None

    salary_from = vacancy.get("payment_from") or None
    salary_to = vacancy.get("payment_to") or None

    return predict_salary(salary_from, salary_to)


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

        while page < SUPERJOB_MAX_PAGES:
            params = {
                "keyword": language,
                "town": SUPERJOB_MOSCOW_CITY_ID,
                "catalogues": SUPERJOB_PROGRAMMING_CATEGORY_ID,
                "count": SUPERJOB_PAGE_SIZE,
                "page": page,
            }

            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=REQUEST_TIMEOUT_SECONDS,
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
