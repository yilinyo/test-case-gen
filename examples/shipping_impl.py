def shipping_fee(weight: int, is_member: bool) -> int:
    if weight <= 0:
        return -1

    if is_member and weight <= 5:
        return 0

    if weight <= 1:
        return 5

    if weight <= 5:
        return 10

    if weight <= 20:
        return 20

    return 50
