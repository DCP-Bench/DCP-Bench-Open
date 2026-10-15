# Travelling salesman: find the shortest route that visits each city exactly once
# and returns to the origin city. The distance between two cities is the Euclidean
# distance between their locations, rounded to an integer. Output: the optimal
# travel distance.
#
# Encoding: a one-hot position pos[i][k] says city i is visited k-th on the route.
# The route starts at city 0 (the origin), which is fixed at position 0. The
# successor Bool e[i][j] says city j is visited right after city i. Successors
# follow the positions, so the route is a single cycle through all cities.
import math
from paramita.modelling import Bool, Or


def build(instance):
    locs = instance["locations"]
    n = len(locs)
    # distance between cities i and j: Euclidean distance rounded to an integer,
    # computed from the instance locations
    dist = [[round(math.hypot(locs[i][0] - locs[j][0], locs[i][1] - locs[j][1]))
             for j in range(n)] for i in range(n)]

    pos = [[Bool(f"pos_{i}_{k}") for k in range(n)] for i in range(n)]
    succ = {(i, j): Bool(f"succ_{i}_{j}") for i in range(n) for j in range(n) if i != j}

    cons = []
    # the origin city 0 is the first city of the route
    cons.append(pos[0][0])
    # each city is visited at exactly one position
    cons += [sum(pos[i]) == 1 for i in range(n)]
    # each position holds exactly one city
    cons += [sum(pos[i][k] for i in range(n)) == 1 for k in range(n)]
    # each city has exactly one next city (leaves the route once)
    cons += [sum(succ[i, j] for j in range(n) if j != i) == 1 for i in range(n)]
    # each city has exactly one previous city (enters the route once)
    cons += [sum(succ[i, j] for i in range(n) if i != j) == 1 for j in range(n)]
    # if j is visited right after i, then j sits at the position after i's position
    # (the last position is followed by the first; this closes the route)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            for k in range(n):
                cons.append(Or([~succ[i, j], ~pos[i][k], pos[j][(k + 1) % n]]))

    # total distance: sum of the distances of the chosen successor pairs,
    # grouped as one row sum per city
    row_sums = [sum(dist[i][j] * succ[i, j] for j in range(n) if j != i) for i in range(n)]
    total = sum(row_sums)

    return cons, {"travel_distance": total}, ("minimize", total)
