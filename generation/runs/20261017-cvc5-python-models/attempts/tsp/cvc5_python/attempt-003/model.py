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

    max_d = max(max(row) for row in dist)

    # Edge variables: x[i, j] is true when the route goes directly from city i to city j.
    x = {(i, j): cz.Bool(f"x_{i}_{j}") for i in range(n) for j in range(n) if i != j}
    # Visit position of each city; the origin city 0 is at position 0.
    pos = [cz.Int(f"pos_{i}") for i in range(n)]
    total = cz.Int("total")
    cons = []

    # Each city is left exactly once.
    for i in range(n):
        cons.append(cz.Sum([cz.If(x[i, j], 1, 0) for j in range(n) if j != i]) == 1)

    # Each city is entered exactly once.
    for j in range(n):
        cons.append(cz.Sum([cz.If(x[i, j], 1, 0) for i in range(n) if i != j]) == 1)

    # The route is one tour through all cities: positions increase along each leg that
    # does not return to the origin, which rules out subtours.
    cons.append(pos[0] == 0)
    for i in range(n):
        cons += [pos[i] >= 0, pos[i] <= n - 1]
    for i in range(1, n):
        cons.append(pos[i] >= 1)
    for i in range(n):
        for j in range(1, n):
            if i != j:
                cons.append(cz.Implies(x[i, j], pos[j] >= pos[i] + 1))

    # The travel distance is the sum of the lengths of the legs taken.
    cons.append(total == cz.Sum([cz.If(x[i, j], dist[i][j], 0) for (i, j) in x]))
    cons += [total >= 0, total <= n * max_d]

    # Each city leaves once, so the tour is at least the sum of the cheapest leg out of
    # each city. Each city is also entered once, so it is at least the cheapest leg in.
    lb_out = sum(min(dist[i][j] for j in range(n) if j != i) for i in range(n))
    lb_in = sum(min(dist[i][j] for i in range(n) if i != j) for j in range(n))
    cons.append(total >= max(lb_out, lb_in))

    return cons, {"travel_distance": total}, ("minimize", total)
