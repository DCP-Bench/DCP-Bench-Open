# Travelling salesman: find the shortest closed route that visits every city
# exactly once and returns to the start. The distance between two cities is the
# Euclidean distance between their locations rounded to an integer.
import math

import z3


def build(instance):
    locations = instance["locations"]  # (x, y) of each city
    n = len(locations)

    # rounded Euclidean distance between every pair of distinct cities
    distance = [
        [int(round(math.hypot(locations[i][0] - locations[j][0], locations[i][1] - locations[j][1]))) if i != j else 0
         for j in range(n)]
        for i in range(n)
    ]

    solver = z3.Solver()

    # go[i][j] is true when the route travels directly from city i to city j
    go = [[z3.Bool(f"go_{i}_{j}") if i != j else None for j in range(n)] for i in range(n)]
    for i in range(n):
        # every city is left exactly once ...
        solver.add(z3.PbEq([(go[i][j], 1) for j in range(n) if j != i], 1))
        # ... and entered exactly once
        solver.add(z3.PbEq([(go[j][i], 1) for j in range(n) if j != i], 1))

    # The arcs must form one circuit, not several. Z3 has no circuit constraint,
    # so each city gets its position on the route; city 0 is first and every arc
    # into another city moves one position on.
    position = [z3.Int(f"position_{i}") for i in range(n)]
    solver.add(position[0] == 0)
    for i in range(1, n):
        solver.add(position[i] >= 1, position[i] <= n - 1)
    for i in range(n):
        for j in range(1, n):
            if i != j:
                solver.add(z3.Implies(go[i][j], position[j] == position[i] + 1))

    # travel_distance = length of the route, to be minimised
    travel_distance = z3.Int("travel_distance")
    solver.add(travel_distance == z3.Sum([z3.If(go[i][j], distance[i][j], 0)
                                          for i in range(n) for j in range(n) if i != j]))

    return solver, {"travel_distance": travel_distance}, ("minimize", travel_distance)
