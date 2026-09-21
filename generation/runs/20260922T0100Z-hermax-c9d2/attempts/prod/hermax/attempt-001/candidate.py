# Most profitable production plan under one shared capacity limit.
from dcp_maxsat import MaxSat


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

    sat = MaxSat()
    x = [sat.int(0, u[j]) for j in range(n)]

    # sum((1/a[j]) * x[j]) <= b, multiplied through by lcm(a) to stay integral.
    scale = 1
    for value in a:
        scale = scale // gcd(scale, value) * value
    sat.weighted_sum_le([scale // value for value in a], x, b * scale)

    ceiling = sum(profit[j] * u[j] for j in range(n))
    total = sat.int(0, ceiling)
    sat.link_sum(list(zip(profit, x)), total)
    return sat, {"x": x, "total_profit": total}, ("maximize", total)
