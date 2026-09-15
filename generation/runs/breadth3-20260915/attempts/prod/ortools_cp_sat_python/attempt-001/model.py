import math

from ortools.sat.python import cp_model


def build(instance):
    a, c, u, b = instance["a"], instance["c"], instance["u"], instance["b"]
    n = len(a)
    model = cp_model.CpModel()
    x = [model.new_int_var(0, max(u), f"x_{j}") for j in range(n)]
    # The reference clears the divisions by scaling with the least common multiple.
    lcm = math.lcm(*a)
    model.add(sum((lcm // a[j]) * x[j] for j in range(n)) <= b * lcm)
    for j in range(n):
        model.add(x[j] <= u[j])
    profit = sum(c[j] * x[j] for j in range(n))
    model.maximize(profit)
    return model, {"x": x, "total_profit": profit}
