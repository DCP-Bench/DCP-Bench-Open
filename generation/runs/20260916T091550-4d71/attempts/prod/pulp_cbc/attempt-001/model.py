import math

import pulp


def build(instance):
    """Production planning: choose quantities within per-product ceilings so
    that the shared production rate constraint holds, maximizing profit.
    """
    a = instance["a"]
    c = instance["c"]
    u = instance["u"]
    b = instance["b"]
    num_products = len(a)
    max_u = max(u)

    problem = pulp.LpProblem("prod", pulp.LpMaximize)
    x = [pulp.LpVariable(f"x{j}", 0, max_u, cat="Integer") for j in range(num_products)]

    # The rate constraint is sum(x[j] / a[j]) <= b.  Multiplying through by the
    # least common multiple of a clears the divisions without rounding.
    lcm_a = 1
    for value in a:
        lcm_a = lcm_a * value // math.gcd(lcm_a, value)
    problem += pulp.lpSum((lcm_a // a[j]) * x[j] for j in range(num_products)) <= b * lcm_a

    for j in range(num_products):
        problem += x[j] <= u[j]

    profit_bound = sum(c[j] * u[j] for j in range(num_products))
    total_profit = pulp.LpVariable("total_profit", 0, profit_bound, cat="Integer")
    problem += total_profit == pulp.lpSum(c[j] * x[j] for j in range(num_products))
    problem += total_profit

    return problem, {"x": x, "total_profit": total_profit}
