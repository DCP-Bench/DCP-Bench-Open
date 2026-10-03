# Revenue maximization: flight legs have limited seats and each package of itineraries
# (a set of legs) is sold at a given price with an estimated demand. Decide how many
# units of each package to sell so that no leg sells more seats than it has and the
# revenue is as large as possible.
from pychoco.model import Model


def build(instance):
    available_seats = instance["available_seats"]  # available_seats[j] = seats on flight leg j
    demand = instance["demand"]  # demand[i] = estimated demand for package i
    revenue = instance["revenue"]  # revenue[i] = revenue of selling one unit of package i
    delta = instance["delta"]  # delta[i][j] = 1 if package i uses flight leg j
    num_packages = len(demand)
    num_legs = len(available_seats)

    model = Model()

    # packages_to_sell[i] = units of package i sold; no more than its demand
    packages_to_sell = [model.intvar(0, demand[i], name=f"packages_to_sell_{i}") for i in range(num_packages)]

    # capacity of each flight leg: the seats taken by all packages that use the leg
    # do not exceed the seats available on it
    for j in range(num_legs):
        model.scalar(packages_to_sell, [delta[i][j] for i in range(num_packages)], "<=", available_seats[j]).post()

    # total revenue (Choco maximises one variable, so it gets its own)
    max_revenue = model.intvar(0, sum(revenue[i] * demand[i] for i in range(num_packages)), name="max_revenue")
    model.scalar(packages_to_sell, revenue, "=", max_revenue).post()

    return model, {"packages_to_sell": packages_to_sell, "max_revenue": max_revenue}, ("maximize", max_revenue)
