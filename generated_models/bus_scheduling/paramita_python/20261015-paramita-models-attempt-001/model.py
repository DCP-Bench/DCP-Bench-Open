# Bus scheduling: minimum number of buses for a day split into 6 successive
# 4-hour intervals. Each bus runs 8 successive hours, so a bus that starts in
# interval i covers intervals i and i+1 (the day wraps around, interval 5 is
# followed by interval 0).
from paramita.modelling import Bool, If


def build(instance):
    demands = instance["demands"]
    n = len(demands)
    # A bus-start count above the largest demand is never needed: capping every
    # x[i] at max(demands) keeps all demand constraints satisfied.
    ub = max(demands)

    # x[i] = number of buses starting in interval i, written in unary:
    # ge[i][k] is true exactly when x[i] >= k + 1.
    ge = [[Bool(f"x_{i}_ge_{k + 1}") for k in range(ub)] for i in range(n)]
    cons = []
    # order: x[i] >= k + 1 implies x[i] >= k
    for i in range(n):
        for k in range(ub - 1):
            cons.append(If(ge[i][k + 1], ge[i][k]))

    x = [sum(ge[i]) for i in range(n)]

    # the number of buses in interval i meets the demand of interval i:
    # buses starting in i or in the previous interval (wrapping) cover i
    for i in range(n):
        prev = (i - 1) % n
        cons.append(sum(ge[i]) + sum(ge[prev]) >= demands[i])

    # minimise the total number of buses scheduled
    total = sum(x)

    return cons, {"x": x}, ("minimize", total)
