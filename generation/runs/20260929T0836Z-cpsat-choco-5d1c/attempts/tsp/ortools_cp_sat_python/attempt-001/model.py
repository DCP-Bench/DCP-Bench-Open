# Travelling salesman: find the shortest closed route that visits every city
# exactly once and returns to the start. The distance between two cities is the
# Euclidean distance between their locations rounded to an integer.
import math

from ortools.sat.python import cp_model


def build(instance):
    locations = instance["locations"]  # (x, y) of each city
    n = len(locations)

    # rounded Euclidean distance between every pair of distinct cities
    distance = [
        [int(round(math.hypot(locations[i][0] - locations[j][0], locations[i][1] - locations[j][1]))) if i != j else 0
         for j in range(n)]
        for i in range(n)
    ]

    model = cp_model.CpModel()

    # go[i][j] is true when the route travels directly from city i to city j
    go = {(i, j): model.new_bool_var(f"go_{i}_{j}") for i in range(n) for j in range(n) if i != j}
    # the arcs taken form one circuit through all cities
    model.add_circuit([(i, j, lit) for (i, j), lit in go.items()])

    # travel_distance = length of the route, to be minimised
    travel_distance = model.new_int_var(0, sum(max(row) for row in distance), "travel_distance")
    model.add(travel_distance == sum(distance[i][j] * lit for (i, j), lit in go.items()))
    model.minimize(travel_distance)

    return model, {"travel_distance": travel_distance}
