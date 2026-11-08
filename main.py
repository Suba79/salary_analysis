
import time

import requests
from terminaltables import AsciiTable

from salary import predict_salary
from superjob import get_superjob_statistics


LANGUAGES = [
    "Python", "Java", "JavaScript", "C++", "C#",
    "PHP", "Go", "TypeScript", "Kotlin", "Ruby",
]

HABR_MOSCOW_CITY_ID = 678
REQUEST_TIMEOUT_SECONDS = 30
HABR_REQUEST_DELAY_SECONDS = 2
HABR_RETRY_DELAY_SECONDS = 5
HABR_MAX_REQUEST_ATTEMPTS = 3


def predict_rub_salary_for_habr(vacancy):
    salary = vacancy.get("salary") or {}

    if salary.get("currency") != "rur":
        return None

    salary_from = salary.get("from")
    salary_to = salary.get("to")

    return predict_salary(salary_from, salary_to)


def get_habr_statistics(languages):
    url = "https://career.habr.com/api/frontend/vacancies"
    statistics = {}

    for language in languages:
        total_salary = 0
        vacancies_processed = 0
        page = 1

        while True:
            params = {
                "q": f"Программист {language}",
                "city_id": HABR_MOSCOW_CITY_ID,
                "page": page,
            }

            time.sleep(HABR_REQUEST_DELAY_SECONDS)

            for attempt in range(1, HABR_MAX_REQUEST_ATTEMPTS + 1):
                try:
                    response = requests.get(
                        url,
                        params=params,
                        timeout=REQUEST_TIMEOUT_SECONDS,
                    )
                    response.raise_for_status()
                    break
                except requests.RequestException:
                    if attempt == HABR_MAX_REQUEST_ATTEMPTS:
                        raise
                    time.sleep(HABR_RETRY_DELAY_SECONDS)

            data = response.json()

            if page == 1:
                vacancies_found = data["meta"]["totalResults"]

            for vacancy in data["list"]:
                salary = predict_rub_salary_for_habr(vacancy)

                if salary is not None:
                    total_salary += salary
                    vacancies_processed += 1

            if not data["list"] or page >= data["meta"]["totalPages"]:
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


def print_statistics_table(statistics, title):
    table_data = [
        [
            "Язык программирования",
            "Вакансий найдено",
            "Вакансий обработано",
            "Средняя зарплата",
        ]
    ]

    for language, data in statistics.items():
        table_data.append([
            language,
            data["vacancies_found"],
            data["vacancies_processed"],
            data["average_salary"],
        ])

    print(AsciiTable(table_data, title).table)


def main():
    habr_statistics = get_habr_statistics(LANGUAGES)
    superjob_statistics = get_superjob_statistics(LANGUAGES)

    print_statistics_table(habr_statistics, "Habr Moscow")
    print()
    print_statistics_table(superjob_statistics, "SuperJob Moscow")


if __name__ == "__main__":
    main()
