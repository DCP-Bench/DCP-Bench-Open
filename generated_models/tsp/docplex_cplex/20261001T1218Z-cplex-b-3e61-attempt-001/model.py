"""Travelling salesman: find the shortest round trip that visits every city exactly once and returns
to its start, with distances the Euclidean distances between the cities rounded to integers.

The model reports the length of the shortest round trip.
"""
import math

from docplex.mp.model import Model


def build(instance):
    locations = instance["locations"]
    n = len(locations)
    cities = range(n)

    # Distance between two cities: Euclidean distance rounded to an integer, as the reference
    # computes it (Python's round).
    dist = [[int(round(math.hypot(a[0] - b[0], a[1] - b[1]))) if i != j else 0
             for j, b in enumerate(locations)] for i, a in enumerate(locations)]

    model = Model("tsp")

    # nxt[i, j] = 1 when city j is visited immediately after city i.
    arcs = [(i, j) for i in cities for j in cities if i != j]
    nxt = {(i, j): model.binary_var(name=f"next_{i}_{j}") for (i, j) in arcs}

    # Every city is left once and entered once.
    for i in cities:
        model.add_constraint(model.sum(nxt[i, j] for j in cities if j != i) == 1)
        model.add_constraint(model.sum(nxt[j, i] for j in cities if j != i) == 1)

    # The trip is a single circuit: order[i] is the position of city i on the trip counted
    # from city 0, and it grows by one along every arc not returning to city 0 (Miller-Tucker-
    # Zemlin constraints, lifted by Desrochers and Laporte). This needs one constraint per arc,
    # which keeps 30 cities inside the Community Edition's 1000 variables and constraints.
    if n > 2:
        order = {i: model.integer_var(1, n - 1, name=f"order_{i}") for i in cities if i != 0}
        for i in cities:
            for j in cities:
                if i != j and i != 0 and j != 0:
                    model.add_constraint(order[i] - order[j] + (n - 1) * nxt[i, j]
                                         + (n - 3) * nxt[j, i] <= n - 2)

    # The travel distance is the sum of the distances of the arcs taken; minimize it.
    travel_distance = model.integer_var(0, sum(map(sum, dist)), name="travel_distance")
    model.add_constraint(travel_distance == model.sum(dist[i][j] * nxt[i, j] for (i, j) in arcs))
    model.minimize(travel_distance)

    return model, {"travel_distance": travel_distance}
