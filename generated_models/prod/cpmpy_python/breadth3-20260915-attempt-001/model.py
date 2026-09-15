import math

import cpmpy as cp


def build(instance):
    a, c, u, b = instance["a"], instance["c"], instance["u"], instance["b"]
    n = len(a)
    x = cp.intvar(0, max(u), shape=n, name="x")
    model = cp.Model()
    # The reference clears the divisions by scaling with the least common multiple.
    lcm = math.lcm(*a)
    model += cp.sum([(lcm // a[j]) * x[j] for j in range(n)]) <= b * lcm
    for j in range(n):
        model += x[j] <= u[j]
    profit = cp.sum([c[j] * x[j] for j in range(n)])
    model.maximize(profit)
    return model, {"x": [x[j] for j in range(n)], "total_profit": profit}
