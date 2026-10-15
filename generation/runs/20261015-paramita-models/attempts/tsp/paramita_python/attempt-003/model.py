# Travelling salesman: find the shortest route that visits each city exactly once
# and returns to the origin city. The distance between two cities is the Euclidean
# distance between their locations, rounded to an integer. Output: the optimal
# travel distance.
#
# Encoding: succ[i][j] says city j is visited right after city i. Each city has one
# next city and one previous city. Subtours are ruled out with an order: each city i
# has a unary position u_i (ge[i][k] means u_i >= k, with ge[i][k+1] -> ge[i][k]).
# The origin city 0 has position 0, and when j follows i (j not the origin) the
# position of j is at least one more than the position of i. A cycle that avoids the
# origin would need its positions to increase all the way round, which is impossible.
from paramita.modelling import Bool, Or


def build(instance):
    locs = instance["locations"]
    n = len(locs)
    # distance between cities i and j: Euclidean distance rounded to an integer,
    # computed from the instance locations
    dist = [[round(((locs[i][0] - locs[j][0]) ** 2 + (locs[i][1] - locs[j][1]) ** 2) ** 0.5)
             for j in range(n)] for i in range(n)]

    succ = {(i, j): Bool(f"succ_{i}_{j}") for i in range(n) for j in range(n) if i != j}
    # ge[i][k] for k = 1..n-1: the position of city i is at least k
    ge = [[None] + [Bool(f"ge_{i}_{k}") for k in range(1, n)] for i in range(n)]

    cons = []
    # the origin city 0 is the first city of the route: position 0 (no ge bit set)
    cons += [~ge[0][k] for k in range(1, n)]
    # positions are unary: a position at least k implies at least k-1
    for i in range(n):
        cons += [Or([~ge[i][k + 1], ge[i][k]]) for k in range(1, n - 1)]
    # each city has exactly one next city (leaves the route once)
    cons += [sum(succ[i, j] for j in range(n) if j != i) == 1 for i in range(n)]
    # each city has exactly one previous city (enters the route once)
    cons += [sum(succ[i, j] for i in range(n) if i != j) == 1 for j in range(n)]
    # the city after i comes one position later (the origin is not in this rule);
    # a city at the last position (n-1) has no later position, so it is followed by the origin
    for i in range(n):
        for j in range(1, n):
            if i == j:
                continue
            cons.append(Or([~succ[i, j], ge[j][1]]))
            for k in range(1, n - 1):
                cons.append(Or([~succ[i, j], ~ge[i][k], ge[j][k + 1]]))
            # a city at the last position cannot be followed by a city other than the origin
            cons.append(Or([~succ[i, j], ~ge[i][n - 1]]))
    # the city before the origin is the last position of the route
    for i in range(1, n):
        cons.append(Or([~succ[i, 0], ge[i][n - 1]]))

    # total distance: sum of the distances of the chosen successor pairs,
    # grouped as one row sum per city
    row_sums = [sum(dist[i][j] * succ[i, j] for j in range(n) if j != i) for i in range(n)]
    total = sum(row_sums)

    return cons, {"travel_distance": total}, ("minimize", total)
