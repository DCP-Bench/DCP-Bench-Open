# Bus scheduling problem: find the minimum number of buses for a day split into 6 successive
# 4-hour slots (cyclic). Each bus works 8 successive hours, i.e. two slots. x[i] is the number of
# buses starting in slot i. The buses working in slot t are those starting in slot t or t-1
# (cyclically), and that count must meet the demand of slot t.
import cvc5.pythonic as cz


def build(instance):
    demands = instance["demands"]
    n = len(demands)
    x = [cz.Int(f"x{i}") for i in range(n)]
    total_demand = sum(demands)
    constraints = []

    # The number of buses starting in each slot is a non-negative integer.
    # Any starting count above the total demand is never needed.
    for i in range(n):
        constraints.append(x[i] >= 0)
        constraints.append(x[i] <= total_demand)

    # The number of buses available in each 4-hour interval meets the demand for that interval.
    # Buses transition between intervals, so a bus starting in the previous slot (wrapping around the day) is also on duty.
    for t in range(n):
        prev = (t - 1) % n
        constraints.append(x[t] + x[prev] >= demands[t])

    total = cz.Sum(x)
    return constraints, {"x": x}, ("minimize", total)
