# Revenue maximization: choose how many units of each flight package to sell so that
# total revenue is maximal while the seats on every flight leg are not overbooked.
from pyscipopt import Model, quicksum


def build(instance):
    available_seats = instance["available_seats"]  # seat capacity of each flight leg
    demand = instance["demand"]  # estimated demand for each package (upper bound on units)
    revenue = instance["revenue"]  # price of one unit of each package
    delta = instance["delta"]  # delta[p][l] = 1 if package p uses flight leg l

    num_packages = len(demand)
    num_legs = len(available_seats)

    m = Model()

    # sell[p] = number of units of package p to sell, at most its estimated demand
    sell = [m.addVar(name=f"sell_{p}", vtype="I", lb=0, ub=demand[p]) for p in range(num_packages)]

    # the seats reserved on each leg cannot exceed the seats available on that leg
    for l in range(num_legs):
        # seats of leg l used by all packages that pass through it
        m.addCons(
            quicksum(delta[p][l] * sell[p] for p in range(num_packages)) <= available_seats[l]
        )

    # total revenue of all sold package units
    total_revenue = quicksum(revenue[p] * sell[p] for p in range(num_packages))
    m.setObjective(total_revenue, "maximize")

    outputs = {
        "max_revenue": total_revenue,
        "packages_to_sell": sell,
    }
    return m, outputs
