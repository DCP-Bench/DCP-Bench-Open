# Travelling salesman problem (TSP): find the shortest route that visits every city
# exactly once and returns to the origin city. The distance between two points is the
# Euclidean distance rounded to an integer. Output: travel_distance (minimised).
import math

import cvc5.pythonic as cz


def build(instance):
    pts = instance["locations"]
    n = len(pts)
    # Integer distance matrix from the instance coordinates.
    dist = [
        [
            int(math.sqrt((pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2) + 0.5)
            for j in range(n)
        ]
        for i in range(n)
    ]

    if n <= 1:
        return [], {"travel_distance": 0}, ("minimize", 0)

    succ = [cz.Int(f"succ_{i}") for i in range(n)]
    pos = [cz.Int(f"pos_{i}") for i in range(n)]
    cost = [cz.Int(f"cost_{i}") for i in range(n)]
    total = cz.Int("total")
    cons = []

    # Each city has one successor, which is a different city.
    for i in range(n):
        cons += [succ[i] >= 0, succ[i] <= n - 1, succ[i] != i]

    # Every city is the successor of exactly one city.
    cons.append(cz.Distinct(succ))

    # Visit order: the origin city 0 is at position 0 and the route runs through positions
    # 1 to n-1 in turn, then returns to the origin. This rules out subtours.
    for i in range(n):
        cons += [pos[i] >= 0, pos[i] <= n - 1]
    cons.append(pos[0] == 0)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if j == 0:
                cons.append(cz.Implies(succ[i] == 0, pos[i] == n - 1))
            else:
                cons.append(cz.Implies(succ[i] == j, pos[j] == pos[i] + 1))

    # The length of each leg is the rounded Euclidean distance to the successor.
    for i in range(n):
        for j in range(n):
            if i != j:
                cons.append(cz.Implies(succ[i] == j, cost[i] == dist[i][j]))

    # The travel distance is the sum of the leg lengths.
    cons.append(total == cz.Sum(cost))

    return cons, {"travel_distance": total}, ("minimize", total)
