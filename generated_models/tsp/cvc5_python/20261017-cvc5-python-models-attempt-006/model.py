# Travelling salesman problem (TSP): find the shortest route that visits each city exactly
# once and returns to the origin city. The distance is the Euclidean distance between the
# points rounded to an integer. Output: travel_distance (minimised).
#
# Work done in Python outside the solver (deterministic, derived only from the distance
# matrix, none of it computes the optimum):
#   1. the rounded integer distance matrix;
#   2. an assignment-problem lower bound (Hungarian method) with its dual potentials, which
#      give non-negative reduced costs rc[i][j] = d[i][j] - u[i] - v[j];
#   3. an upper bound UB: the best of nearest-neighbour tours from every start city, each
#      improved by 2-opt moves in a fixed scan order (a feasible tour, so the optimum is
#      at most UB);
#   4. arcs (i, j) with LB + rc[i][j] > UB cannot lie on a tour of length at most UB, so
#      no variable is created for them;
#   5. a Held-Karp 1-tree lower bound (subgradient ascent with a fixed step rule): an edge
#      whose minimum 1-tree with the edge forced in exceeds UB cannot lie on a tour of
#      length at most UB, so neither of its two arcs gets a variable.
# The solver still searches the tours and proves the minimum itself.
import math

import cvc5.pythonic as cz


def _hungarian(a):
    """Min-cost assignment on square matrix a: returns (cost, u, v) with a[i][j]-u[i]-v[j] >= 0."""
    n = len(a)
    INF = 10 ** 9
    u = [0] * (n + 1)
    v = [0] * (n + 1)
    p = [0] * (n + 1)
    way = [0] * (n + 1)
    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [INF] * (n + 1)
        used = [False] * (n + 1)
        while True:
            used[j0] = True
            i0 = p[j0]
            delta = INF
            j1 = 0
            for j in range(1, n + 1):
                if not used[j]:
                    cur = a[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break
    return -v[0], u[1:], v[1:]


def _tour_len(t, d):
    return sum(d[t[k]][t[(k + 1) % len(t)]] for k in range(len(t)))


def _two_opt(t, d):
    n = len(t)
    improved = True
    while improved:
        improved = False
        for i in range(n - 1):
            for j in range(i + 2, n):
                if i == 0 and j == n - 1:
                    continue
                a, b = t[i], t[i + 1]
                c, e = t[j], t[(j + 1) % n]
                if d[a][c] + d[b][e] < d[a][b] + d[c][e]:
                    t[i + 1:j + 1] = reversed(t[i + 1:j + 1])
                    improved = True
    return t


def _one_tree(w, n, forced=None):
    """Weight of a minimum 1-tree on symmetric weights w (node 0 special), optionally with
    one edge forced into it."""
    edges = sorted((w[i][j], i, j) for i in range(1, n) for j in range(i + 1, n))
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    total = 0.0
    zero_edges = [(w[0][k], k) for k in range(1, n)]
    deg = [0] * n
    used = []
    forced_zero = None
    if forced is not None:
        a, b = forced
        if a == 0 or b == 0:
            forced_zero = b if a == 0 else a
        else:
            parent[find(a)] = find(b)
            total += w[a][b]
            deg[a] += 1
            deg[b] += 1
            used.append((a, b))
    for wt, i, j in edges:
        if forced is not None and (i, j) == tuple(sorted(forced)) and forced_zero is None:
            continue
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj
            total += wt
            deg[i] += 1
            deg[j] += 1
            used.append((i, j))
    zero_edges.sort()
    if forced_zero is not None:
        total += w[0][forced_zero]
        deg[0] += 1
        deg[forced_zero] += 1
        for wt, k in zero_edges:
            if k != forced_zero:
                total += wt
                deg[0] += 1
                deg[k] += 1
                break
    else:
        for wt, k in zero_edges[:2]:
            total += wt
            deg[0] += 1
            deg[k] += 1
    return total, deg


def _held_karp_pi(d, n, ub):
    """Subgradient ascent on the 1-tree Lagrangian bound with fixed step rule."""
    pi = [0.0] * n
    best_pi = list(pi)
    best_l = -1e18
    lam = 2.0
    stall = 0
    for _ in range(400):
        w = [[d[i][j] + pi[i] + pi[j] for j in range(n)] for i in range(n)]
        t, deg = _one_tree(w, n)
        l_val = t - 2 * sum(pi)
        if l_val > best_l + 1e-9:
            best_l = l_val
            best_pi = list(pi)
            stall = 0
        else:
            stall += 1
            if stall >= 10:
                lam *= 0.7
                stall = 0
        g = [deg[i] - 2 for i in range(n)]
        norm = sum(x * x for x in g)
        if norm == 0 or lam < 1e-4:
            break
        step = lam * max(ub - l_val, 1.0) / norm
        pi = [pi[i] + step * g[i] for i in range(n)]
    return best_pi


def _one_tree_edge_ok(d, n, ub):
    """Set of undirected edges (i<j) that can lie in a tour of length at most ub, by the
    1-tree bound with the edge forced in."""
    pi = _held_karp_pi(d, n, ub)
    w = [[d[i][j] + pi[i] + pi[j] for j in range(n)] for i in range(n)]
    shift = 2 * sum(pi)
    ok = set()
    for i in range(n):
        for j in range(i + 1, n):
            t, _ = _one_tree(w, n, forced=(i, j))
            if math.ceil(t - shift - 1e-6) <= ub:
                ok.add((i, j))
    return ok


def build(instance):
    pts = instance["locations"]
    n = len(pts)
    if n <= 1:
        return [], {"travel_distance": 0}, ("minimize", 0)

    # Integer distance matrix from the instance coordinates.
    d = [
        [
            int(math.sqrt((pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2) + 0.5)
            for j in range(n)
        ]
        for i in range(n)
    ]

    # Python-side bounds (see header).
    big = 10 ** 6
    cost = [[d[i][j] if i != j else big for j in range(n)] for i in range(n)]
    lb, u, v = _hungarian(cost)
    rc = [[cost[i][j] - u[i] - v[j] for j in range(n)] for i in range(n)]
    ub = None
    for s in range(n):
        left = [c for c in range(n) if c != s]
        t = [s]
        while left:
            nxt = min(left, key=lambda c: (d[t[-1]][c], c))
            left.remove(nxt)
            t.append(nxt)
        t = _two_opt(t, d)
        length = _tour_len(t, d)
        if ub is None or length < ub:
            ub = length
    edge_ok = _one_tree_edge_ok(d, n, ub) if n > 3 else None
    arcs = [
        (i, j)
        for i in range(n)
        for j in range(n)
        if i != j
        and lb + rc[i][j] <= ub
        and (edge_ok is None or (min(i, j), max(i, j)) in edge_ok)
    ]
    aset = set(arcs)

    solver = cz.SolverFor("QF_LIA")
    cons = []

    # y[i, j] is 1 when the route goes directly from city i to city j, else 0.
    y = {a: cz.Int(f"y_{a[0]}_{a[1]}") for a in arcs}
    for var in y.values():
        cons += [var >= 0, var <= 1]

    # Each city is left exactly once.
    for i in range(n):
        cons.append(cz.Sum([y[i, j] for j in range(n) if (i, j) in aset]) == 1)

    # Each city is entered exactly once.
    for j in range(n):
        cons.append(cz.Sum([y[i, j] for i in range(n) if (i, j) in aset]) == 1)

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
    for (i, j) in arcs:
        if j == 0:
            continue
        cons.append(cz.Or(y[i, j] == 0, ge[j, 1]))
        if i == 0:
            continue
        for t in range(1, n):
            if t + 1 <= n - 1:
                cons.append(cz.Or(y[i, j] == 0, cz.Not(ge[i, t]), ge[j, t + 1]))
            else:
                cons.append(cz.Or(y[i, j] == 0, cz.Not(ge[i, t])))

    # No two cities are visited back and forth.
    for (i, j) in arcs:
        if i < j and (j, i) in aset:
            cons.append(y[i, j] + y[j, i] <= 1)

    # The travel distance is the sum of the lengths of the legs taken, written with the
    # reduced costs: the assignment bound plus the non-negative reduced cost of each leg.
    total = cz.Int("total")
    cons.append(total == lb + cz.Sum([rc[i][j] * y[i, j] for (i, j) in arcs]))
    cons.append(total >= lb)
    cons.append(total <= ub)

    solver.add(*cons)
    return solver, {"travel_distance": total}, ("minimize", total)
