# Travelling salesman: visit every city exactly once and return to the start
# along the shortest route, distances being Euclidean distances rounded to
# integers. The declared output is the length of that route.
import math

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer


def build(instance):
    locations = instance["locations"]
    n = len(locations)

    # Distances as the reference computes them: Euclidean, rounded.
    dist = [[int(round(math.hypot(a[0] - b[0], a[1] - b[1]))) if i != j else 0
             for j, b in enumerate(locations)] for i, a in enumerate(locations)]

    pool = IDPool()
    formula = WCNF()
    true = pool.id("true")
    formula.append([true])
    false = -true

    # succ[i][j] is true when city j is visited right after city i.
    succ = [[pool.id(("succ", i, j)) if i != j else None for j in range(n)]
            for i in range(n)]

    # Every city has exactly one successor and exactly one predecessor.
    for i in range(n):
        out = [succ[i][j] for j in range(n) if j != i]
        into = [succ[j][i] for j in range(n) if j != i]
        for lits in (out, into):
            if lits:
                formula.extend(CardEnc.equals(lits=lits, bound=1, vpool=pool,
                                              encoding=EncType.seqcounter).clauses)

    # One single circuit, no subtours: city 0 starts the route, and every
    # other city gets a position 1..n-1 that grows by at least one along each
    # step not returning to city 0. A subtour avoiding city 0 would need
    # positions that grow all the way round a cycle, which is impossible.
    pos = {}
    for i in range(1, n):
        if n > 2:
            pos[i] = Integer(f"position_{i}", 1, n - 1, encoding="order", vpool=pool)
            formula.extend(pos[i].domain_clauses())
    if n > 2:
        for i in range(1, n):
            for j in range(1, n):
                if i == j:
                    continue
                for t in range(1, n):
                    # i at position >= t and j after i: j at position >= t + 1.
                    clause = [-succ[i][j]]
                    if t > 1:
                        clause.append(-pos[i].ge(t))
                    if t + 1 <= n - 1:
                        clause.append(pos[j].ge(t + 1))
                    formula.append(clause)

    # Upper bound on the shortest route: the nearest-neighbour tour from city
    # 0. No optimal route is longer, so the length is capped there.
    upper = 0
    here, seen = 0, {0}
    while len(seen) < n:
        nxt = min((j for j in range(n) if j not in seen), key=lambda j: dist[here][j])
        upper += dist[here][nxt]
        seen.add(nxt)
        here = nxt
    upper += dist[here][0]

    # The route length in binary. Each city has exactly one successor, so the
    # length of the step leaving city i has bit k set exactly when the chosen
    # successor's distance has bit k set: an OR of successor literals, no
    # arithmetic needed. The steps are then added with ripple-carry adders.
    width = max(upper.bit_length(), 1)

    def full_adder(x, y, c):
        s, carry = pool.id(), pool.id()
        for vx in (True, False):
            for vy in (True, False):
                for vc in (True, False):
                    odd = vx ^ vy ^ vc
                    formula.append([-x if vx else x, -y if vy else y,
                                    -c if vc else c, s if odd else -s])
        formula.extend([[-x, -y, carry], [-x, -c, carry], [-y, -c, carry],
                        [x, y, -carry], [x, c, -carry], [y, c, -carry]])
        return s, carry

    def add(xs, ys):
        length = max(len(xs), len(ys))
        xs = xs + [false] * (length - len(xs))
        ys = ys + [false] * (length - len(ys))
        out, carry = [], false
        for x, y in zip(xs, ys):
            s, carry = full_adder(x, y, carry)
            out.append(s)
        return out + [carry]

    total = [false]
    for i in range(n):
        top = max([dist[i][j] for j in range(n) if j != i] + [0])
        step = []
        for k in range(max(top.bit_length(), 1)):
            chosen = [succ[i][j] for j in range(n) if j != i and (dist[i][j] >> k) & 1]
            if not chosen:
                step.append(false)
                continue
            bit = pool.id(("step_bit", i, k))
            formula.append([-bit] + chosen)
            for lit in chosen:
                formula.append([-lit, bit])
            step.append(bit)
        total = add(total, step)

    # The length is at most the nearest-neighbour bound: forbid any higher
    # bit pattern (bits above the width are zero; below it, compare).
    for k in range(width, len(total)):
        formula.append([-total[k]])
    bits = total[:width]
    for k in range(width):
        if not (upper >> k) & 1:
            clause = [-bits[k]]
            for j in range(k + 1, width):
                clause.append(-bits[j] if (upper >> j) & 1 else bits[j])
            formula.append(clause)

    # travel_distance, the declared output: an Integer over 0..upper whose
    # value literal is true exactly when the bits spell that value. The bits
    # spell exactly one value in range, so no exactly-one is needed.
    travel_distance = Integer("travel_distance", 0, max(upper, 1), vpool=pool)
    for v in range(0, max(upper, 1) + 1):
        lit = travel_distance.equals(v)
        if v > upper:
            formula.append([-lit])
            continue
        spelled = [bits[k] if (v >> k) & 1 else -bits[k] for k in range(width)]
        for s in spelled:
            formula.append([-lit, s])
        formula.append([lit] + [-s for s in spelled])

    # A route never steps straight back to the city it came from (with more
    # than two cities); implied by the single circuit, stated for the solver.
    if n > 2:
        for i in range(n):
            for j in range(i + 1, n):
                formula.append([-succ[i][j], -succ[j][i]])

    # Minimise the route length: taking the step from i to j pays its
    # distance. Every city is left exactly once and entered exactly once, so
    # subtracting the same amount from every step leaving city i (or every
    # step entering city j) changes every route's length by that same amount
    # and leaves the shortest route where it is. The amounts subtracted are
    # the dual values (row[i], col[j]) of the assignment problem "give every
    # city one successor and one predecessor", computed with the Hungarian
    # method (shortest augmenting paths); they keep every reduced distance
    # dist[i][j] - row[i] - col[j] non-negative and make as many of them
    # zero as an assignment allows. The soft clauses pay those reduced
    # distances. The declared length above is still the true distance.
    big = sum(max(r) for r in dist) + 1  # stands in for the forbidden i -> i
    row = [0] * (n + 1)
    col = [0] * (n + 1)
    match = [0] * (n + 1)  # match[j] = row assigned to column j, 1-based
    for i in range(1, n + 1):
        match[0] = i
        j0 = 0
        least = [float("inf")] * (n + 1)
        via = [0] * (n + 1)
        used = [False] * (n + 1)
        while True:
            used[j0] = True
            i0, delta, j1 = match[j0], float("inf"), 0
            for j in range(1, n + 1):
                if not used[j]:
                    c = (big if i0 == j else dist[i0 - 1][j - 1]) - row[i0] - col[j]
                    if c < least[j]:
                        least[j], via[j] = c, j0
                    if least[j] < delta:
                        delta, j1 = least[j], j
            for j in range(n + 1):
                if used[j]:
                    row[match[j]] += delta
                    col[j] -= delta
                else:
                    least[j] -= delta
            j0 = j1
            if match[j0] == 0:
                break
        while j0:
            j1 = via[j0]
            match[j0] = match[j1]
            j0 = j1
    reduced = [[dist[i][j] - row[i + 1] - col[j + 1] for j in range(n)]
               for i in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j and reduced[i][j] > 0:
                formula.append([-succ[i][j]], weight=reduced[i][j])

    return formula, {"travel_distance": travel_distance}
