
LOWER_SALARY_MULTIPLIER = 1.2
UPPER_SALARY_MULTIPLIER = 0.8


def predict_salary(salary_from, salary_to):
    if salary_from is None and salary_to is None:
        return None

    if salary_from is None:
        return salary_to * UPPER_SALARY_MULTIPLIER

    if salary_to is None:
        return salary_from * LOWER_SALARY_MULTIPLIER

    return (salary_from + salary_to) / 2
