# Travelling salesman: find the shortest route that visits each city exactly once and
# returns to the origin city, where the distance between two cities is the Euclidean
# distance between their locations rounded to an integer. Output: the optimal travel
# distance.
#
# Encoding: succ[i][j] says city j is visited right after city i. Each city has one
# next city and one previous city. A unary position u_i (ge[i][k] means u_i >= k) is
# used to rule out loops that avoid the origin: the origin has position 0, and whenever
# j follows i with j not the origin, u_j >= u_i + 1. Positions only increase along the
# route, so the only cycle that can close is the one through the origin.
# The unary order encoding is used here (not one-hot positions) because the order
# constraints are then clauses over at most three literals.
from paramita.modelling import Bool, Or


def build(instance):
    locs = instance["locations"]
    n = len(locs)
    # distance between cities i and j: Euclidean distance rounded to an integer,
    # computed from the instance locations
    dist = [[round(((locs[i][0] - locs[j][0]) ** 2 + (locs[i][1] - locs[j][1]) ** 2) ** 0.5)
             for j in range(n)] for i in range(n)]

    succ = {(i, j): Bool(f"succ_{i}_{j}") for i in range(n) for j in range(n) if i != j}
    # ge[i][k] for k = 1..n-1: the position of city i in the route is at least k
    ge = [{k: Bool(f"ge_{i}_{k}") for k in range(1, n)} for i in range(n)]

    cons = []
    # the origin city 0 is the first city of the route: position 0
    cons += [~ge[0][k] for k in range(1, n)]
    # the position is unary: a position of at least k+1 implies at least k
    for i in range(n):
        cons += [Or([~ge[i][k + 1], ge[i][k]]) for k in range(1, n - 1)]

    # every city is left exactly once: one next city per city
    cons += [sum(succ[i, j] for j in range(n) if j != i) == 1 for i in range(n)]
    # every city is entered exactly once: one previous city per city
    cons += [sum(succ[i, j] for i in range(n) if i != j) == 1 for j in range(n)]
    # redundant: no two cities are each other's next city (a loop of two cities)
    cons += [Or([~succ[i, j], ~succ[j, i]]) for i in range(n) for j in range(i + 1, n)]

    # the route is one closed loop: if j follows i and j is not the origin, the position
    # of j is at least one more than the position of i
    for i in range(n):
        for j in range(1, n):
            if i == j:
                continue
            cons.append(Or([~succ[i, j], ge[j][1]]))
            for k in range(1, n - 1):
                cons.append(Or([~succ[i, j], ~ge[i][k], ge[j][k + 1]]))
            # the last position cannot be followed by another city than the origin
            cons.append(Or([~succ[i, j], ~ge[i][n - 1]]))

    # total distance: sum of the distances of the chosen successor pairs,
    # grouped as one row sum per city
    row_sums = [sum(dist[i][j] * succ[i, j] for j in range(n) if j != i) for i in range(n)]
    total = sum(row_sums)

    return cons, {"travel_distance": total}, ("minimize", total)
