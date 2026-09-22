# Most profitable production plan under one shared capacity limit.
from math import gcd

from exact import Exact


def build(instance):
    a = instance["a"]
    profit = instance["c"]
    u = instance["u"]
    b = instance["b"]
    n = len(a)

    solver = Exact()
    x = [f"x{j}" for j in range(n)]
    for j, name in enumerate(x):
        solver.addVariable(name, 0, u[j])

    # sum((1/a[j]) * x[j]) <= b, multiplied through by lcm(a) to stay integral.
    scale = 1
    for value in a:
        scale = scale // gcd(scale, value) * value
    solver.addConstraint([(scale // a[j], x[j]) for j in range(n)],
                         False, 0, True, b * scale)

    solver.addVariable("total", 0, sum(profit[j] * u[j] for j in range(n)))
    solver.addConstraint(list(zip(profit, x)) + [(-1, "total")], True, 0, True, 0)
    return (solver, {"x": x, "total_profit": "total"},
            ("maximize", [(1, "total")]))
