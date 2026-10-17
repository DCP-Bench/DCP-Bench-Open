# prod: choose production quantities x[j] for each product j in P to maximise the
# total profit, the sum of c[j] * x[j] over all j, subject to a time budget and bounds.
import math

import cvc5.pythonic as cz


def build(instance):
    a = instance["a"]
    b = instance["b"]
    c = instance["c"]
    u = instance["u"]
    n = len(a)

    # The time budget is multiplied by L = lcm(a) so that every coefficient is an
    # exact integer (1/a[j] * L = L // a[j]).
    L = 1
    for aj in a:
        L = L * aj // math.gcd(L, aj)

    x = [cz.Int(f"x{j}") for j in range(n)]

    constraints = []

    # The sum of (1/a[j]) * x[j] over all j should be less than or equal to b.
    constraints.append(cz.Sum([(L // a[j]) * x[j] for j in range(n)]) <= L * b)

    # x[j] should be between 0 and u[j] for all j.
    for j in range(n):
        constraints.append(x[j] >= 0)
        constraints.append(x[j] <= u[j])

    # The goal is to maximize the total profit, the sum of c[j] * x[j] for all j.
    profit = cz.Sum([c[j] * x[j] for j in range(n)])

    return constraints, {"total_profit": profit, "x": x}, ("maximize", profit)
