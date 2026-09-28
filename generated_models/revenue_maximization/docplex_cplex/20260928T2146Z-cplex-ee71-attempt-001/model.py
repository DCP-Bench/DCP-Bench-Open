"""Airline revenue: choose how many units of each itinerary package to sell, within seats and demand, for maximum revenue."""
from docplex.mp.model import Model


def build(instance):
    seats = instance["available_seats"]
    demand = instance["demand"]
    revenue = instance["revenue"]
    uses = instance["delta"]  # uses[i][j] is 1 if package i flies on leg j
    packages = range(len(demand))
    legs = range(len(seats))

    model = Model("revenue_maximization")

    # packages_to_sell[i] is how many units of package i are sold; selling no more
    # than the estimated demand is the variable's upper bound.
    packages_to_sell = [model.integer_var(0, demand[i], name=f"packages_to_sell_{i}") for i in packages]

    # The packages sold fit into the seats available on every flight leg.
    for j in legs:
        model.add_constraint(model.sum(uses[i][j] * packages_to_sell[i] for i in packages) <= seats[j],
                             ctname=f"seats_{j}")

    # Maximise the revenue of the packages sold.
    max_revenue = model.dot(packages_to_sell, revenue)
    model.maximize(max_revenue)

    return model, {"packages_to_sell": packages_to_sell, "max_revenue": max_revenue}
