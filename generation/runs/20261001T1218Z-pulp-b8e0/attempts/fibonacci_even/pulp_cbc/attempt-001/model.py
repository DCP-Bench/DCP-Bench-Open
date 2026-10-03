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

    # x[i] = 1 exactly when f[i] is even and below four million
    x = {i: pulp.LpVariable(f"x_{i}", cat="Binary") for i in terms}
    for i in terms:
        # even: f[i] = 2 * half + odd, with odd = 0
        half = pulp.LpVariable(f"half_{i}", 0, term_top // 2, cat="Integer")
        odd = pulp.LpVariable(f"odd_{i}", cat="Binary")
        problem += f[i] == 2 * half + odd
        # small = 1 exactly when f[i] < limit
        small = pulp.LpVariable(f"small_{i}", cat="Binary")
        problem += f[i] <= limit - 1 + term_top * (1 - small)
        problem += f[i] >= limit - term_top * small
        # x = small and not odd
        problem += x[i] <= small
        problem += x[i] <= 1 - odd
        problem += x[i] >= small - odd

    # res is the sum of the terms selected by x; picked[i] is x[i] * f[i], linearized
    # with the term bound 10^7
    res = pulp.LpVariable("res", 0, res_top, cat="Integer")
    picked = {i: pulp.LpVariable(f"picked_{i}", 0, term_top) for i in terms}
    for i in terms:
        problem += picked[i] <= term_top * x[i]
        problem += picked[i] <= f[i]
        problem += picked[i] >= f[i] - term_top * (1 - x[i])
    problem += res == pulp.lpSum(picked.values())

    return problem, {"res": res}
