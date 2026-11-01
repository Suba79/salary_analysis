
import time

import requests
from terminaltables import AsciiTable

from superjob import get_superjob_statistics


LANGUAGES = [
    "Python", "Java", "JavaScript", "C++", "C#",
    "PHP", "Go", "TypeScript", "Kotlin", "Ruby",
]


def predict_rub_salary_for_habr(vacancy):
    salary = vacancy.get("salary") or {}

    if salary.get("currency") != "rur":
        return None

    salary_from = salary.get("from")
    salary_to = salary.get("to")

    if salary_from is None and salary_to is None:
        return None
    if salary_from is None:
        return salary_to * 0.8
    if salary_to is None:
        return salary_from * 1.2

    return (salary_from + salary_to) / 2


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
                "city_id": 678,
                "page": page,
            }

            time.sleep(2)

            for attempt in range(3):
                try:
                    response = requests.get(
                        url, params=params, timeout=30
                    )
                    response.raise_for_status()
                    break
                except requests.RequestException:
                    if attempt == 2:
                        raise
                    time.sleep(5)

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
