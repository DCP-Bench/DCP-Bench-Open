"""Travelling salesman: the shortest round trip that visits every city exactly once and returns to the origin."""
import math

import gurobipy as gp
from gurobipy import GRB


def build(instance):
    locations = instance["locations"]
    n = len(locations)
    cities = range(n)

    # Distance between two cities: Euclidean distance rounded to an integer.
    dist = [[int(round(math.hypot(a[0] - b[0], a[1] - b[1]))) if i != j else 0
             for j, b in enumerate(locations)] for i, a in enumerate(locations)]

    model = gp.Model("tsp")

    # arc[i, j] is 1 when city j is visited immediately after city i.
    arc = model.addVars([(i, j) for i in cities for j in cities if i != j], vtype=GRB.BINARY, name="arc")

    # Every city is left once and entered once.
    for i in cities:
        model.addConstr(arc.sum(i, "*") == 1, name=f"leave[{i}]")
        model.addConstr(arc.sum("*", i) == 1, name=f"enter[{i}]")

    # The successors form one circuit through all cities: position[i] is the place of
    # city i in the tour after city 0, and it grows by one along every arc that does
    # not return to city 0, so no closed sub-tour avoids city 0 (Miller-Tucker-Zemlin;
    # n - 1 bounds the position difference).
    position = model.addVars(cities, lb=0, ub=n - 1, vtype=GRB.CONTINUOUS, name="position")
    model.addConstr(position[0] == 0, name="origin")
    for (i, j) in arc.keys():
        if j != 0:
            model.addConstr(position[j] >= position[i] + 1 - n * (1 - arc[i, j]), name=f"order[{i},{j}]")

    # The travel distance is the sum of the distances of the arcs taken; minimise it.
    travel_distance = model.addVar(lb=0, ub=sum(max(row) for row in dist), vtype=GRB.INTEGER,
                                   name="travel_distance")
    model.addConstr(travel_distance == gp.quicksum(dist[i][j] * arc[i, j] for (i, j) in arc.keys()),
                    name="distance")
    model.setObjective(travel_distance, GRB.MINIMIZE)

    return model, {"travel_distance": travel_distance}
