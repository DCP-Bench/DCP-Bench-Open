# Travelling salesman: find the shortest closed route that visits every city
# exactly once and returns to the start. The distance between two cities is the
# Euclidean distance between their locations rounded to an integer.
import math

from pychoco.model import Model


def build(instance):
    locations = instance["locations"]  # (x, y) of each city
    n = len(locations)

    # rounded Euclidean distance between every pair of distinct cities
    distance = [
        [int(round(math.hypot(locations[i][0] - locations[j][0], locations[i][1] - locations[j][1]))) if i != j else 0
         for j in range(n)]
        for i in range(n)
    ]

    model = Model()

    # successor[i] = the city visited right after city i; together they form one circuit
    successor = [model.intvar(0, n - 1, name=f"successor_{i}") for i in range(n)]
    model.circuit(successor).post()

    # the distance travelled from city i to its successor, looked up in row i of the distance matrix
    legs = []
    for i in range(n):
        leg = model.intvar(min(distance[i]), max(distance[i]), name=f"leg_{i}")
        model.element(leg, distance[i], successor[i]).post()
        legs.append(leg)

    # travel_distance = length of the route, to be minimised
    travel_distance = model.intvar(0, sum(max(row) for row in distance), name="travel_distance")
    model.sum(legs, "=", travel_distance).post()

    return model, {"travel_distance": travel_distance}, ("minimize", travel_distance)
