"""Divisible by 1 through 9 (and 10): find a 10-digit number that uses each digit 0..9 once,
where the number formed by its first n digits is divisible by n for every n.

The model reports the number.
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data

    length = 10
    places = range(length)
    digits = range(10)

    problem = pulp.LpProblem("divisible_by_1_through_9", pulp.LpMinimize)  # satisfaction

    # is_digit[i][v] = 1 if the digit at place i (from the left) is v; every place has one
    # digit and every digit is used exactly once
    is_digit = [[pulp.LpVariable(f"is_digit_{i}_{v}", cat="Binary") for v in digits]
                for i in places]
    for i in places:
        problem += pulp.lpSum(is_digit[i]) == 1
    for v in digits:
        problem += pulp.lpSum(is_digit[i][v] for i in places) == 1
    x = [pulp.lpSum(v * is_digit[i][v] for v in digits) for i in places]

    # The number formed by the first i + 1 digits is divisible by i + 1. Only its remainder
    # matters, so each digit is weighted by 10^(i - j) mod (i + 1) rather than 10^(i - j);
    # this keeps every coefficient small instead of reaching 10^9, which a floating-point
    # solver cannot hold exactly. The weighted sum is then a multiple of i + 1.
    for i in places:
        divisor = i + 1
        weights = [pow(10, i - j, divisor) for j in range(i + 1)]
        largest = sum(w * 9 for w in weights)
        multiple = pulp.LpVariable(f"multiple_{i}", 0, largest // divisor, cat="Integer")
        problem += pulp.lpSum(w * x[j] for j, w in enumerate(weights)) == divisor * multiple

    # the number read from its ten digits
    number = pulp.lpSum(10 ** (length - 1 - i) * x[i] for i in places)
    return problem, {"number": number}
