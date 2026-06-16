def password_strength(password: str) -> str:
    if len(password) < 6:
        return "weak"

    has_digit = False
    has_letter = False

    for char in password:
        if char.isdigit():
            has_digit = True
        if char.isalpha():
            has_letter = True

    if has_digit and has_letter and len(password) >= 10:
        return "strong"

    if has_digit and has_letter:
        return "medium"

    return "weak"
