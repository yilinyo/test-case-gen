def is_leap_year(year: int) -> bool:
    if year <= 0:
        return False

    if year % 400 == 0:
        return True

    if year % 100 == 0:
        return False

    if year % 4 == 0:
        return True

    return False


def days_in_month(year: int, month: int) -> int:
    if month < 1 or month > 12:
        return 0

    if month == 2:
        if is_leap_year(year):
            return 29
        return 28

    if month == 4 or month == 6 or month == 9 or month == 11:
        return 30

    return 31
