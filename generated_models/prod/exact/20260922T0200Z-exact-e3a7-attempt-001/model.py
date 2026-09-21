# Most profitable production plan under one shared capacity limit.
from dcp_pb import Pb


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

    pb = Pb()
    x = [pb.int(0, u[j]) for j in range(n)]

    # sum((1/a[j]) * x[j]) <= b, multiplied through by lcm(a) to stay integral.
    scale = 1
    for value in a:
        scale = scale // gcd(scale, value) * value
    pb.le([(scale // a[j], x[j]) for j in range(n)], b * scale)

    total = pb.int(0, sum(profit[j] * u[j] for j in range(n)))
    pb.eq(list(zip(profit, x)) + [(-1, total)], 0)
    pb.maximise([(1, total)])
    return pb, {"x": x, "total_profit": total}
