# Most profitable production plan under one shared capacity limit.
from hermax.model import Model


def gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a)


def build(instance):
    a = instance["a"]
    profit = instance["c"]
    u = instance["u"]
    b = instance["b"]
    n = len(a)

    m = Model()
    x = [m.int(f"x_{j}", 0, u[j]) for j in range(n)]

    # sum((1/a[j]) * x[j]) <= b, multiplied through by lcm(a) to stay integral.
    scale = 1
    for value in a:
        scale = scale // gcd(scale, value) * value
    m &= (sum((scale // a[j]) * x[j] for j in range(n)) <= b * scale)

    ceiling = sum(profit[j] * u[j] for j in range(n))
    total = m.int("total_profit", 0, ceiling)
    m &= (sum(profit[j] * x[j] for j in range(n)) == total)
    m.obj += ceiling - total
    return m, {"x": x, "total_profit": total}
