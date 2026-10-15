# Travelling salesman: the shortest tour that visits every city once and returns to the origin city,
# where the distance between two cities is the Euclidean distance rounded to an integer.
import math

from pyscipopt import Model, quicksum


def build(instance):
    locations = instance["locations"]
    n = len(locations)

    model = Model()

    # distance between two cities: the Euclidean distance between the points, rounded to an integer
    dist = {}
    for i in range(n):
        for j in range(n):
            if i != j:
                dx = locations[i][0] - locations[j][0]
                dy = locations[i][1] - locations[j][1]
                dist[i, j] = round(math.sqrt(dx * dx + dy * dy))

    # x[i, j] = 1 if the tour travels directly from city i to city j
    x = {(i, j): model.addVar(name=f"x_{i}_{j}", vtype="B") for (i, j) in dist}

    # each city is left exactly once
    for i in range(n):
        model.addCons(quicksum(x[i, j] for j in range(n) if j != i) == 1)

    # each city is entered exactly once
    for j in range(n):
        model.addCons(quicksum(x[i, j] for i in range(n) if i != j) == 1)

    # no subtours: u[i] is the position of city i on the tour, with the origin city 0 at position 0
    # (Miller-Tucker-Zemlin constraints: u[i] - u[j] + (n - 1) * x[i, j] <= n - 2 for i, j >= 1)
    u = {}
    for i in range(1, n):
        u[i] = model.addVar(name=f"u_{i}", vtype="I", lb=1, ub=n - 1)
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                model.addCons(u[i] - u[j] + (n - 1) * x[i, j] <= n - 2)

    # the travel distance is the total distance of the chosen legs
    travel_distance = quicksum(dist[i, j] * x[i, j] for (i, j) in dist)
    model.setObjective(travel_distance, "minimize")

    return model, {"travel_distance": travel_distance}
