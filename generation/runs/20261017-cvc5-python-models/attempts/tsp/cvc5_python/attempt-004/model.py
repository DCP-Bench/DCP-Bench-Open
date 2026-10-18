# Travelling salesman problem (TSP): find the shortest route that visits each city exactly
# once and returns to the origin city. The distance is the Euclidean distance between the
# points rounded to an integer. Output: travel_distance (minimised).
import math

import cvc5.pythonic as cz


def build(instance):
    pts = instance["locations"]
    n = len(pts)
    if n <= 1:
        return [], {"travel_distance": 0}, ("minimize", 0)

    # Integer distance matrix from the instance coordinates.
    dist = [
        [
            int(math.sqrt((pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2) + 0.5)
            for j in range(n)
        ]
        for i in range(n)
    ]

    solver = cz.SolverFor("QF_LIA")
    cons = []

    # y[i, j] is 1 when the route goes directly from city i to city j, else 0. Degree rows
    # are linear, so the solver sees the assignment relaxation of the tour.
    y = {(i, j): cz.Int(f"y_{i}_{j}") for i in range(n) for j in range(n) if i != j}
    for v in y.values():
        cons += [v >= 0, v <= 1]

    # Each city is left exactly once.
    for i in range(n):
        cons.append(cz.Sum([y[i, j] for j in range(n) if j != i]) == 1)

    # Each city is entered exactly once.
    for j in range(n):
        cons.append(cz.Sum([y[i, j] for i in range(n) if i != j]) == 1)

    # The route visits every city once: the visit position of city i is held in an
    # order encoding, ge[i][t] meaning "position of city i is at least t".
    # The origin city 0 is at position 0; every other city is at a position in 1..n-1.
    ge = {}
    for i in range(1, n):
        for t in range(1, n):
            ge[i, t] = cz.Bool(f"ge_{i}_{t}")
        cons.append(ge[i, 1])
        for t in range(1, n - 1):
            cons.append(cz.Or(cz.Not(ge[i, t + 1]), ge[i, t]))

    # A route that goes from city i to city j (j not the origin) puts j after i:
    # if i is at position p, then j is at a position of at least p + 1.
    for i in range(n):
        for j in range(1, n):
            if i == j:
                continue
            # Threshold 0: the position of i is always at least 0.
            cons.append(cz.Or(y[i, j] == 0, ge[j, 1]))
            if i == 0:
                continue
            for t in range(1, n):
                # Position n-1 leaves no later position, so the arc is then ruled out.
                if t + 1 <= n - 1:
                    cons.append(cz.Or(y[i, j] == 0, cz.Not(ge[i, t]), ge[j, t + 1]))
                else:
                    cons.append(cz.Or(y[i, j] == 0, cz.Not(ge[i, t])))

    # No two cities are visited back and forth.
    for i in range(n):
        for j in range(i + 1, n):
            cons.append(y[i, j] + y[j, i] <= 1)

    # The travel distance is the sum of the lengths of the legs taken.
    total = cz.Int("total")
    cons.append(total == cz.Sum([dist[i][j] * y[i, j] for (i, j) in y]))

    # Each city leaves once, so the tour is at least the sum of the cheapest leg out of
    # each city. Each city is also entered once, so it is at least the cheapest leg in.
    lb_out = sum(min(dist[i][j] for j in range(n) if j != i) for i in range(n))
    lb_in = sum(min(dist[i][j] for i in range(n) if i != j) for j in range(n))
    cons.append(total >= max(lb_out, lb_in))

    solver.add(*cons)
    return solver, {"travel_distance": total}, ("minimize", total)
