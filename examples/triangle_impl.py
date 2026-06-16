def check_triangle(d1: int, d2: int, d3: int) -> str:
    if d1 <= 0 or d2 <= 0 or d3 <= 0:
        return "non-triangle"

    if d1 + d2 <= d3 or d1 + d3 <= d2 or d2 + d3 <= d1:
        return "non-triangle"

    if d1 == d2 and d2 == d3:
        return "equilateral triangle"

    if d1 == d2 or d1 == d3 or d2 == d3:
        return "isosceles triangle"

    return "other triangle"
