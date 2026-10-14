"""Bank card PIN: a four-digit PIN abcd with no repeated digit, where the two-digit number
cd is three times ab and da is twice bc.

The model reports the digits a, b, c, d.
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data

    names = ["a", "b", "c", "d"]
    digits = range(10)

    problem = pulp.LpProblem("bank_card", pulp.LpMinimize)  # satisfaction

    # is_digit[name][v] = 1 if that PIN digit is v; no two digits are the same
    is_digit = {x: [pulp.LpVariable(f"is_{x}_{v}", cat="Binary") for v in digits] for x in names}
    for x in names:
        problem += pulp.lpSum(is_digit[x]) == 1
    for v in digits:
        problem += pulp.lpSum(is_digit[x][v] for x in names) <= 1
    a, b, c, d = (pulp.lpSum(v * is_digit[x][v] for v in digits) for x in names)

    # the 2-digit number cd is 3 times the 2-digit number ab
    problem += 10 * c + d == 3 * (10 * a + b)
    # the 2-digit number da is 2 times the 2-digit number bc
    problem += 10 * d + a == 2 * (10 * b + c)

    return problem, {"a": a, "b": b, "c": c, "d": d}
