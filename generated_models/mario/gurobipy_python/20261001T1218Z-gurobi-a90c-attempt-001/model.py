"""Mario: route from Mario's house to Luigi's house within a fuel limit, collecting as much gold as possible."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["nHouses"]
    mario = instance["marioHouse"]
    luigi = instance["luigiHouse"]
    fuel_limit = instance["fuelLimit"]
    arc_fuel = instance["arc_fuel"]
    gold = instance["goldInHouse"]
    houses = range(n)

    model = gp.Model("mario")

    # arc[i, j] is 1 when house j succeeds house i; arc[i, i] is 1 when house i
    # is not part of the route.
    arc = model.addVars(houses, houses, vtype=GRB.BINARY, name="arc")

    # Every house has exactly one successor, and the successors are all
    # different (a permutation of the houses).
    for i in houses:
        model.addConstr(arc.sum(i, "*") == 1, name=f"succ[{i}]")
    for j in houses:
        model.addConstr(arc.sum("*", j) == 1, name=f"pred[{j}]")

    # The route closes from Luigi's house back to Mario's house.
    model.addConstr(arc[luigi, mario] == 1, name="luigi_to_mario")

    # Mario's house is on the route: the reference gives it rank 1, and a house
    # off the route must rank after Luigi's house, which is impossible for rank 1.
    model.addConstr(arc[mario, mario] == 0, name="mario_on_route")

    # Rank of each house along the route, 1 at Mario's house. Along every arc that
    # does not return to Mario's house the rank grows by one, so the only cycle
    # that is not a self-loop is the route through Mario's house (Miller-Tucker-
    # Zemlin subtour elimination; n bounds the rank difference).
    order = model.addVars(houses, lb=1, ub=n, vtype=GRB.CONTINUOUS, name="order")
    model.addConstr(order[mario] == 1, name="mario_rank")
    for i in houses:
        for j in houses:
            if i != j and j != mario:
                model.addConstr(order[j] >= order[i] + 1 - n * (1 - arc[i, j]), name=f"rank[{i},{j}]")

    # The fuel used on the arcs of the route stays within the fuel limit.
    model.addConstr(gp.quicksum(arc_fuel[i][j] * arc[i, j] for i in houses for j in houses) <= fuel_limit,
                    name="fuel")

    # Gold is earned at every house on the route (successor different from itself).
    model.setObjective(gp.quicksum(gold[i] * (1 - arc[i, i]) for i in houses), GRB.MAXIMIZE)

    # s[i]: the house succeeding house i, i itself when i is not on the route.
    s = [gp.quicksum(j * arc[i, j] for j in houses) for i in houses]
    return model, {"s": s}
