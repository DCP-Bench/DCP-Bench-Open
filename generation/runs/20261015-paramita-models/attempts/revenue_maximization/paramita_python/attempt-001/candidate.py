# Revenue maximization over flight legs and itinerary packages.
# Each package is sold in units; one unit of package p reserves one seat on every leg that p uses.

from paramita.modelling import Bool, If


def build(instance):
    seats = instance["available_seats"]
    demand = instance["demand"]
    revenue = instance["revenue"]
    delta = instance["delta"]  # delta[p][l] = 1 when package p uses leg l
    n_legs = len(seats)
    n_pkgs = len(demand)

    # Unary (order) encoding of the units sold of each package: u[p][i] is true
    # when more than i units of package p are sold. The bits run to the package
    # demand, so the units sold never exceed the demand.
    u = [[Bool(f"u_{p}_{i}") for i in range(demand[p])] for p in range(n_pkgs)]

    cons = []

    # units are counted in order: selling i+1 units of a package requires selling i units
    for p in range(n_pkgs):
        for i in range(demand[p] - 1):
            cons.append(If(u[p][i + 1], u[p][i]))

    # the seats reserved on each leg (one per unit of every package using the leg)
    # fit within the available seats of that leg
    for l in range(n_legs):
        bits = [b for p in range(n_pkgs) if delta[p][l] for b in u[p]]
        if bits:
            cons.append(sum(bits) <= seats[l])

    # total revenue: each unit sold of package p earns revenue[p]; this is the objective
    total = sum(revenue[p] * b for p in range(n_pkgs) for b in u[p])

    # number of units sold of each package
    packages_to_sell = [sum(u[p]) for p in range(n_pkgs)]

    return cons, {"max_revenue": total, "packages_to_sell": packages_to_sell}, ("maximize", total)
