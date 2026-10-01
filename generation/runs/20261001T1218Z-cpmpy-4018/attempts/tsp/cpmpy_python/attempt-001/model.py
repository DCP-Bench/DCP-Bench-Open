# Travelling salesman problem: find the shortest closed route that visits every city exactly
# once; the distance between two cities is their Euclidean distance rounded to an integer.
import math

import cpmpy as cp


def build(instance):
    locations = instance["locations"]  # (x, y) coordinates of each city
    n = len(locations)

    # dist[i][j] = Euclidean distance between city i and city j, rounded to an integer
    dist = [[int(round(math.hypot(a[0] - b[0], a[1] - b[1]))) if i != j else 0
             for j, b in enumerate(locations)]
            for i, a in enumerate(locations)]

    # nxt[i] = j means the route goes from city i directly to city j
    nxt = cp.intvar(0, n - 1, shape=(n,), name="nxt")

    model = cp.Model()

    # The successors form one single circuit through all the cities.
    model += cp.Circuit(nxt)

    # Total length of the route. Encoding choice: the length is a sum over arc indicators
    # (nxt[i] == j) times the distance. This linear form gives the solver a much better bound
    # than looking the distance up with a variable index (dist[i][nxt[i]]).
    # Upper bound: every city leaves along its longest arc.
    travel_distance = cp.intvar(0, sum(max(row) for row in dist), name="travel_distance")
    model += travel_distance == cp.sum([dist[i][j] * (nxt[i] == j)
                                        for i in range(n) for j in range(n) if i != j])

    # Minimise the length of the route.
    model.minimize(travel_distance)

    return model, {"travel_distance": travel_distance}
