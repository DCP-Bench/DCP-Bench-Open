# Travelling salesman: find the shortest route that visits each city exactly once and
# returns to the origin city, where the distance between two cities is the Euclidean
# distance between their locations rounded to an integer. Output: the optimal travel
# distance.
#
# Encoding: succ[i, j] says city j is visited right after city i. A unary position
# ge[i][k] (city i is at position >= k) rules out loops that avoid the origin.
# Objective: every tour uses exactly one arc leaving each city and one arc entering each
# city, so the row minimum and then the column minimum of the distance matrix can be
# subtracted from the arc costs and added back as a constant. The shifted costs have many
# zeros and small weights, which gives MaxSAT a strong first lower bound (the assignment
# bound) and fewer distinct weights; the optimum is unchanged.
from paramita.modelling import Bool, Or


def build(instance):
    locs = instance["locations"]
    n = len(locs)
    # distance between cities i and j: Euclidean distance rounded to an integer,
    # computed from the instance locations
    dist = [[round(((locs[i][0] - locs[j][0]) ** 2 + (locs[i][1] - locs[j][1]) ** 2) ** 0.5)
             for j in range(n)] for i in range(n)]

    # shift the costs: subtract the cheapest arc leaving each city, then the cheapest
    # arc entering each city (diagonal excluded); every route pays the subtracted total
    cost = [row[:] for row in dist]
    constant = 0
    for i in range(n):
        m = min(cost[i][j] for j in range(n) if j != i)
        constant += m
        for j in range(n):
            if j != i:
                cost[i][j] -= m
    for j in range(n):
        m = min(cost[i][j] for i in range(n) if i != j)
        constant += m
        for i in range(n):
            if i != j:
                cost[i][j] -= m

    succ = {(i, j): Bool(f"succ_{i}_{j}") for i in range(n) for j in range(n) if i != j}
    # ge[i][k] for k = 1..n-1: the position of city i in the route is at least k
    ge = [{k: Bool(f"ge_{i}_{k}") for k in range(1, n)} for i in range(n)]

    cons = []
    # the origin city 0 is the first city of the route: position 0
    cons += [~ge[0][k] for k in range(1, n)]
    # the position is unary: a position of at least k+1 implies at least k
    for i in range(n):
        cons += [Or([~ge[i][k + 1], ge[i][k]]) for k in range(1, n - 1)]

    # visits each city exactly once: one next city per city
    cons += [sum(succ[i, j] for j in range(n) if j != i) == 1 for i in range(n)]
    # visits each city exactly once: one previous city per city
    cons += [sum(succ[i, j] for i in range(n) if i != j) == 1 for j in range(n)]
    # redundant: no two cities are each other's next city (a loop of two cities)
    cons += [Or([~succ[i, j], ~succ[j, i]]) for i in range(n) for j in range(i + 1, n)]

    # returns to the origin city as one closed loop: if j follows i and j is not the
    # origin, the position of j is at least one more than the position of i
    for i in range(n):
        for j in range(1, n):
            if i == j:
                continue
            cons.append(Or([~succ[i, j], ge[j][1]]))
            for k in range(1, n - 1):
                cons.append(Or([~succ[i, j], ~ge[i][k], ge[j][k + 1]]))
            # the last position cannot be followed by another city than the origin
            cons.append(Or([~succ[i, j], ~ge[i][n - 1]]))

    # total distance: the subtracted constant plus the shifted cost of the chosen arcs
    total = constant + sum(cost[i][j] * succ[i, j] for i in range(n) for j in range(n)
                           if i != j and cost[i][j] > 0)

    return cons, {"travel_distance": total}, ("minimize", total)
