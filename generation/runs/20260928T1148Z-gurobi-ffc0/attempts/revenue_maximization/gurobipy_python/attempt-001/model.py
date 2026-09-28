"""Airline revenue: choose how many units of each itinerary package to sell, within seats and demand, for maximum revenue."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    seats = instance["available_seats"]
    demand = instance["demand"]
    revenue = instance["revenue"]
    uses = instance["delta"]  # uses[i][j] is 1 if package i flies on leg j
    packages = range(len(demand))
    legs = range(len(seats))

    model = gp.Model("revenue_maximization")

    # packages_to_sell[i] is how many units of package i are sold; selling no more
    # than the estimated demand is the variable's upper bound.
    packages_to_sell = model.addVars(packages, lb=0, vtype=GRB.INTEGER, name="packages_to_sell")
    for i in packages:
        packages_to_sell[i].UB = demand[i]

    # The packages sold fit into the seats available on every flight leg.
    for j in legs:
        model.addConstr(gp.quicksum(uses[i][j] * packages_to_sell[i] for i in packages) <= seats[j],
                        name=f"seats[{j}]")

    # Maximise the revenue of the packages sold.
    max_revenue = gp.quicksum(revenue[i] * packages_to_sell[i] for i in packages)
    model.setObjective(max_revenue, GRB.MAXIMIZE)

    return model, {"packages_to_sell": [packages_to_sell[i] for i in packages],
                   "max_revenue": max_revenue}
