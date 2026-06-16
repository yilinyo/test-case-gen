def classify_number(n: int) -> str:
    if n < 0:
        return "negative"

    if n == 0:
        return "zero"

    if n % 2 == 0:
        return "positive even"

    return "positive odd"


def absolute_value(n: int) -> int:
    if n < 0:
        return -n

    return n
