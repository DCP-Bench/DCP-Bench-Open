import pulp


def build(instance):
    """ISBN-13: recover the digits marked -1, respecting the 978/979 prefix and
    the weighted check-digit rule.
    """
    isbn_init = instance["isbn_init"]
    n = len(isbn_init)

    problem = pulp.LpProblem("isbn", pulp.LpMinimize)
    digits = [pulp.LpVariable(f"d{i}", 0, 9, cat="Integer") for i in range(n)]

    # Anything not marked -1 is already known.
    for i, known in enumerate(isbn_init):
        if known != -1:
            problem += digits[i] == known

    # ISBN-13 prefixes: 978 or 979.  These belong to the numbering scheme rather
    # than the instance, and the reference fixes them the same way.
    problem += digits[0] == 9
    problem += digits[1] == 7
    problem += digits[2] >= 8

    # Check digit: 10 minus the weighted sum mod 10, itself taken mod 10.  With
    # no modulo operator, the remainder is written as check_sum - 10 * quotient
    # with the remainder boxed into 0..9.
    weighted = pulp.lpSum((1 if i % 2 == 0 else 3) * digits[i] for i in range(n - 1))
    largest = 9 * 3 * (n - 1)
    quotient = pulp.LpVariable("quotient", 0, largest // 10 + 1, cat="Integer")
    remainder = pulp.LpVariable("remainder", 0, 9, cat="Integer")
    problem += weighted == 10 * quotient + remainder

    # The outer mod 10 only matters when the remainder is zero, where the check
    # digit is zero rather than ten; zero_remainder is the indicator for that.
    zero_remainder = pulp.LpVariable("zero_remainder", cat="Binary")
    problem += remainder <= 9 * (1 - zero_remainder)
    problem += remainder >= 1 - zero_remainder
    problem += digits[n - 1] == 10 - remainder - 10 * zero_remainder

    return problem, {"isbn": digits}
