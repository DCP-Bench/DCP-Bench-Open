# Sell the mix of packages that earns most without overbooking any leg.
#
# Exact takes integer variables natively, so the revenue total needs no
# encoding and the wide range that defeated the one-hot integrations costs
# nothing here.
from exact import Exact


def build(instance):
    seats = instance["available_seats"]
    demand = instance["demand"]
    revenue = instance["revenue"]
    delta = instance["delta"]
    packages, legs = len(demand), len(seats)

    solver = Exact()
    sell = [f"sell{i}" for i in range(packages)]
    for i, name in enumerate(sell):
        solver.addVariable(name, 0, demand[i])
    for j in range(legs):
        solver.addConstraint([(delta[i][j], sell[i]) for i in range(packages)
                              if delta[i][j]], False, 0, True, seats[j])

    ceiling = sum(revenue[i] * demand[i] for i in range(packages))
    solver.addVariable("earned", 0, ceiling)
    solver.addConstraint(list(zip(revenue, sell)) + [(-1, "earned")],
                         True, 0, True, 0)
    return (solver, {"packages_to_sell": sell, "max_revenue": "earned"},
            ("maximize", [(1, "earned")]))
