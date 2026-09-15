import math

import z3


def build(instance):
    a, c, u, b = instance["a"], instance["c"], instance["u"], instance["b"]
    n = len(a)
    x = [z3.Int(f"x_{j}") for j in range(n)]
    constraints = [v >= 0 for v in x] + [v <= max(u) for v in x]
    # The reference clears the divisions by scaling with the least common multiple.
    lcm = math.lcm(*a)
    constraints.append(z3.Sum([(lcm // a[j]) * x[j] for j in range(n)]) <= b * lcm)
    constraints += [x[j] <= u[j] for j in range(n)]
    profit = z3.Sum([c[j] * x[j] for j in range(n)])
    return constraints, {"x": x, "total_profit": profit}, ("maximize", profit)
