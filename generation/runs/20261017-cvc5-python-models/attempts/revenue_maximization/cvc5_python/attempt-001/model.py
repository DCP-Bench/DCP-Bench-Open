# Revenue maximization: flight legs with limited seats, packages of itineraries
# with a price and an estimated demand. Choose how many units of each package to
# sell so that the total revenue is maximal, while the seats of every leg are
# reserved for the packages sold.
import cvc5.pythonic as cz


def build(instance):
    seats = instance["available_seats"]
    demand = instance["demand"]
    revenue = instance["revenue"]
    delta = instance["delta"]  # delta[p][l] = 1 if package p uses leg l

    n_packages = len(demand)
    n_legs = len(seats)

    x = [cz.Int(f"x{p}") for p in range(n_packages)]

    constraints = []

    # Each package has an estimated demand: the units sold cannot exceed it.
    for p in range(n_packages):
        constraints.append(x[p] >= 0)
        constraints.append(x[p] <= demand[p])

    # We reserve the passenger seats according to the number of packages we want
    # to sell: the seats used on each leg cannot exceed the leg's capacity.
    for l in range(n_legs):
        using = [p for p in range(n_packages) if delta[p][l]]
        if using:
            constraints.append(cz.Sum([x[p] for p in using]) <= seats[l])

    # Maximize the total revenue of the packages sold.
    total = cz.Sum([revenue[p] * x[p] for p in range(n_packages)])

    outputs = {
        "max_revenue": total,
        "packages_to_sell": x,
    }
    return constraints, outputs, ("maximize", total)
