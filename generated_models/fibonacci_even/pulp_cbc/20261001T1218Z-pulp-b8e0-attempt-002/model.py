"""Even Fibonacci numbers (Project Euler 2): the sum of the even-valued terms of the
Fibonacci sequence that do not exceed four million.

The model reports the sum (res).
"""
import pulp


def build(instance):
    del instance  # the problem has no instance data; its bounds are below

    # Problem constants, mirrored from the reference: terms f[1..35], each in 0..10^7, the
    # limit of four million, and the sum in 0..10^8.
    n = 35
    term_top = 10 ** 7
    limit = 4000000
    res_top = 10 ** 8
    terms = range(1, n + 1)

    problem = pulp.LpProblem("fibonacci_even", pulp.LpMinimize)  # satisfaction

    # f[i] is the i-th Fibonacci term: 0, 1, 1, then each the sum of the two before
    f = [pulp.LpVariable(f"f_{i}", 0, term_top, cat="Integer") for i in range(n + 1)]
    problem += f[0] == 0
    problem += f[1] == 1
    problem += f[2] == 1
    for i in range(3, n + 1):
        problem += f[i] == f[i - 1] + f[i - 2]

    # odd[i] = 1 if f[i] is odd: f[i] = 2 * half + odd
    odd = [pulp.LpVariable(f"odd_{i}", cat="Binary") for i in range(n + 1)]
    for i in range(n + 1):
        half = pulp.LpVariable(f"half_{i}", 0, term_top // 2, cat="Integer")
        problem += f[i] == 2 * half + odd[i]
    # Implied by the recurrence, stated so the solver needs no search to find parities: a
    # term is odd exactly when one of the two terms before it is (odd = xor of those two).
    for i in range(3, n + 1):
        a, b, c = odd[i - 1], odd[i - 2], odd[i]
        problem += c <= a + b
        problem += c >= a - b
        problem += c >= b - a
        problem += c <= 2 - a - b

    # small[i] = 1 exactly when f[i] is below four million
    small = {i: pulp.LpVariable(f"small_{i}", cat="Binary") for i in terms}
    for i in terms:
        problem += f[i] <= limit - 1 + (term_top - limit + 1) * (1 - small[i])
        problem += f[i] >= limit - limit * small[i]
    # Implied: from f[2] on the terms never decrease, so once a term reaches the limit
    # every later one does too.
    for i in range(3, n + 1):
        problem += small[i] <= small[i - 1]

    # x[i] = 1 exactly when f[i] is even and below four million
    x = {i: pulp.LpVariable(f"x_{i}", cat="Binary") for i in terms}
    for i in terms:
        problem += x[i] <= small[i]
        problem += x[i] <= 1 - odd[i]
        problem += x[i] >= small[i] - odd[i]

    # res is the sum of the terms selected by x; picked[i] is x[i] * f[i], linearized. A
    # selected term is below the limit, so limit - 1 bounds picked[i]; term_top bounds the
    # gap when x[i] = 0.
    res = pulp.LpVariable("res", 0, res_top, cat="Integer")
    picked = {i: pulp.LpVariable(f"picked_{i}", 0, limit - 1, cat="Integer") for i in terms}
    for i in terms:
        problem += picked[i] <= (limit - 1) * x[i]
        problem += picked[i] <= f[i]
        problem += picked[i] >= f[i] - term_top * (1 - x[i])
    problem += res == pulp.lpSum(picked.values())

    return problem, {"res": res}
