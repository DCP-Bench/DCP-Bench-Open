# Travelling salesman: find the shortest closed route that visits every city
# exactly once and returns to the start. The distance between two cities is the
# Euclidean distance between their locations rounded to an integer.
#
# The model is purely Boolean (arc literals, order-encoded positions, cardinality
# constraints) and the route length is a weighted sum of arc literals, so Z3's
# optimiser can treat the objective as weighted MaxSAT over its SAT core instead of
# searching with integer arithmetic. An earlier version with integer positions and
# an integer length variable did not prove the optimum for 12 cities in 180 s.
import math

import z3


def build(instance):
    locations = instance["locations"]  # (x, y) of each city
    n = len(locations)

    # rounded Euclidean distance between every pair of cities, as the problem defines it
    dist = [[int(round(math.hypot(a[0] - b[0], a[1] - b[1]))) if i != j else 0
             for j, b in enumerate(locations)] for i, a in enumerate(locations)]

    if n == 1:
        # a single city: the route stays where it is
        return [], {"travel_distance": 0}, ("minimize", z3.IntVal(0))

    # ---- Bounds computed from the instance (plain Python, before Z3 runs) ----

    def route_length(route):
        return sum(dist[route[k]][route[(k + 1) % n]] for k in range(n))

    # Upper bound: the best nearest-neighbour route over all start cities, improved
    # by 2-opt moves (reverse a segment when that shortens the route). Any route is
    # an upper bound on the shortest one.
    best_route = None
    for start in range(n):
        route, seen = [start], {start}
        while len(route) < n:
            here = route[-1]
            nxt = min((j for j in range(n) if j not in seen), key=lambda j: dist[here][j])
            route.append(nxt)
            seen.add(nxt)
        improved = True
        while improved:
            improved = False
            for a in range(n - 1):
                for b in range(a + 2, n):
                    p, q = route[a], route[a + 1]
                    r, s = route[b], route[(b + 1) % n]
                    if p == s:
                        continue
                    if dist[p][r] + dist[q][s] < dist[p][q] + dist[r][s]:
                        route[a + 1:b + 1] = reversed(route[a + 1:b + 1])
                        improved = True
        if best_route is None or route_length(route) < route_length(best_route):
            best_route = route
    upper = route_length(best_route)

    # Lower bound and reduced distances: every route leaves each city once and enters
    # each city once, so it is an assignment of successors. Solving that assignment
    # problem (Hungarian method, shortest augmenting paths) gives values row[i] and
    # col[j] with dist[i][j] - row[i] - col[j] >= 0 for every arc. Because each city is
    # left once and entered once, every route's length equals
    #     sum(row) + sum(col) + (sum of the reduced distances of its arcs),
    # so the objective below is the exact route length, and sum(row) + sum(col) is a
    # lower bound on it.
    big = sum(max(r) for r in dist) + 1  # stands in for the forbidden arc i -> i
    row = [0] * (n + 1)
    col = [0] * (n + 1)
    owner = [0] * (n + 1)  # owner[j] = row (1-based) assigned to column j
    for i in range(1, n + 1):
        owner[0] = i
        j0 = 0
        least = [math.inf] * (n + 1)
        via = [0] * (n + 1)
        used = [False] * (n + 1)
        while True:
            used[j0] = True
            i0, delta, j1 = owner[j0], math.inf, 0
            for j in range(1, n + 1):
                if not used[j]:
                    c = (big if i0 == j else dist[i0 - 1][j - 1]) - row[i0] - col[j]
                    if c < least[j]:
                        least[j], via[j] = c, j0
                    if least[j] < delta:
                        delta, j1 = least[j], j
            for j in range(n + 1):
                if used[j]:
                    row[owner[j]] += delta
                    col[j] -= delta
                else:
                    least[j] -= delta
            j0 = j1
            if owner[j0] == 0:
                break
        while j0:
            j1 = via[j0]
            owner[j0] = owner[j1]
            j0 = j1
    lower = sum(row[1:]) + sum(col[1:])
    reduced = [[dist[i][j] - row[i + 1] - col[j + 1] for j in range(n)] for i in range(n)]

    solver = z3.Solver()

    # succ[i][j] is true when the route goes directly from city i to city j.
    succ = [[z3.Bool(f"succ_{i}_{j}") if i != j else None for j in range(n)] for i in range(n)]
    arcs = [(i, j) for i in range(n) for j in range(n) if i != j]

    # Every city is left exactly once and entered exactly once.
    for i in range(n):
        solver.add(z3.PbEq([(succ[i][j], 1) for j in range(n) if j != i], 1))
        solver.add(z3.PbEq([(succ[j][i], 1) for j in range(n) if j != i], 1))

    # The route is one circuit through all cities, not several smaller ones.
    if n > 2:
        # With more than two cities a route never steps straight back to the city it
        # came from (implied by the single circuit; stated for the solver).
        for i in range(n):
            for j in range(i + 1, n):
                solver.add(z3.Or(z3.Not(succ[i][j]), z3.Not(succ[j][i])))

        # City 0 is at position 0 and every other city has a position 1 .. n-1 on the
        # route, its place in the visiting order. at_least[i][t] means "city i is at
        # position t or later" (order encoding, t = 2 .. n-1; position >= 1 always
        # holds and position >= n never does).
        def at_least(i, t):
            if t <= 1:
                return z3.BoolVal(True)
            if t >= n:
                return z3.BoolVal(False)
            return ge[i][t]

        ge = {i: {t: z3.Bool(f"pos_{i}_ge_{t}") for t in range(2, n)} for i in range(1, n)}
        for i in range(1, n):
            for t in range(2, n - 1):
                solver.add(z3.Implies(ge[i][t + 1], ge[i][t]))

        for i in range(1, n):
            # leaving city 0 for city i makes i the first city after 0 ...
            solver.add(z3.Implies(succ[0][i], z3.Not(at_least(i, 2))))
            # ... and returning to city 0 from city i makes i the last one
            solver.add(z3.Implies(succ[i][0], at_least(i, n - 1)))
        # Going from city i to city j (neither is city 0) puts j one position after i.
        # A subtour avoiding city 0 would need positions that grow all the way round a
        # cycle, which is impossible.
        for i in range(1, n):
            for j in range(1, n):
                if i != j:
                    for t in range(1, n):
                        solver.add(z3.Implies(succ[i][j], at_least(i, t) == at_least(j, t + 1)))

        # Each position 1 .. n-1 holds exactly one city (implied by the positions being
        # the visiting order; stated for the solver).
        for t in range(1, n):
            solver.add(z3.PbEq([(z3.And(at_least(i, t), z3.Not(at_least(i, t + 1))), 1)
                                for i in range(1, n)], 1))

        # Symmetry breaking (the modeller's own; the reference has none): a route and
        # the same route travelled backwards have the same length. Reversing a route
        # maps position t to n - t, which swaps the order of cities 1 and 2, so
        # requiring city 1 before city 2 keeps exactly one direction of each route.
        # The only declared output is the length, which both directions share.
        for t in range(1, n):
            solver.add(z3.Implies(at_least(1, t), at_least(2, t + 1)))

    # Reduced-cost fixing: a route that uses arc (i, j) has length at least
    # lower + reduced[i][j], because every reduced distance is non-negative. When that
    # exceeds the upper bound, no shortest route uses the arc, so it is excluded. Both
    # directions of every shortest route keep all their arcs.
    slack = upper - lower
    for i, j in arcs:
        if reduced[i][j] > slack:
            solver.add(z3.Not(succ[i][j]))

    # The route is no longer than the upper bound found above.
    weighted = [(succ[i][j], reduced[i][j]) for i, j in arcs if reduced[i][j] > 0]
    if weighted:
        solver.add(z3.PbLe(weighted, slack))

    # travel_distance = the length of the route, to be minimised: the lower bound plus
    # the reduced distances of the arcs used (equal to the plain sum of distances, see
    # above). Written as a sum of If(arc, weight, 0) terms so Z3 can minimise it as
    # weighted MaxSAT.
    travel_distance = z3.Sum([z3.IntVal(lower)] + [z3.If(lit, w, 0) for lit, w in weighted])

    return solver, {"travel_distance": travel_distance}, ("minimize", travel_distance)
