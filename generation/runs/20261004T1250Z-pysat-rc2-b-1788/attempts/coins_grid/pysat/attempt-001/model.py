# Coins grid (Hurlimann's SVOR 2007 coin puzzle): place coins on an n by n
# grid, at most one per cell, exactly c in every row and every column, so that
# the sum of the squared horizontal distances of the coins from the main
# diagonal is as small as possible.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]
    c = instance["c"]

    pool = IDPool()
    # x[i][j] is 1 when a coin lies on cell (i, j); a 0/1 Integer so it prints
    # as a number, with its "== 1" literal used in the clauses below.
    x = [[Integer(f"x_{i}_{j}", 0, 1, vpool=pool) for j in range(n)] for i in range(n)]
    coin = [[x[i][j].equals(1) for j in range(n)] for i in range(n)]
    # dist[i][j] is the squared horizontal distance of cell (i, j) from the diagonal.
    dist = [[(i - j) * (i - j) for j in range(n)] for i in range(n)]

    # Upper bound on z. The circulant placement, a coin on (i, j) exactly
    # when (j - i + c // 2) mod n < c, has c coins in every row and column, so
    # the optimum costs at most what it costs. Values above it can never be
    # optimal, which keeps z's domain and the running sum below small.
    bound = sum(dist[i][j] for i in range(n) for j in range(n)
                if (j - i + c // 2) % n < c)
    z = Integer("z", 0, max(bound, 1), vpool=pool)

    engine = IntegerEngine(vars=[v for row in x for v in row] + [z], vpool=pool)
    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # In each row exactly c coins are placed.
    for i in range(n):
        formula.extend(CardEnc.equals(lits=coin[i], bound=c, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)
    # In each column exactly c coins are placed.
    for j in range(n):
        formula.extend(CardEnc.equals(lits=[coin[i][j] for i in range(n)], bound=c,
                                      vpool=pool, encoding=EncType.seqcounter).clauses)

    # z is the sum of the squared distances of the cells holding a coin. It is
    # tied to the coins by a running sum over the off-diagonal cells, one
    # literal per partial sum up to the bound; a linear constraint on z would
    # hand the encoder hundreds of weighted literals for z's values instead.
    # Unit propagation fixes z once the coins are placed.
    start = pool.id(("partial", 0, 0))
    formula.append([start])
    partial = {0: start}
    cells = [(i, j) for i in range(n) for j in range(n) if dist[i][j] > 0]
    for k, (i, j) in enumerate(cells):
        d = dist[i][j]
        nxt = {}
        for v in partial:
            for w in (v, v + d):
                if w <= bound and w not in nxt:
                    nxt[w] = pool.id(("partial", k + 1, w))
        for v, lit in partial.items():
            # no coin on (i, j): the sum stays at v
            formula.append([-lit, coin[i][j], nxt[v]])
            # a coin on (i, j): the sum grows by d, and may not pass the bound
            if v + d <= bound:
                formula.append([-lit, -coin[i][j], nxt[v + d]])
            else:
                formula.append([-lit, -coin[i][j]])
        partial = nxt
    # The final partial sum is z; z takes exactly one value, so exactly one
    # partial sum is true at every step.
    for v, lit in partial.items():
        formula.append([-lit, z.equals(v)])
    for v in range(0, max(bound, 1) + 1):
        if v not in partial:
            formula.append([-z.equals(v)])

    # Minimise z: a coin on cell (i, j) pays its squared distance.
    for (i, j) in cells:
        formula.append([-coin[i][j]], weight=dist[i][j])

    return formula, {"x": x, "z": z}
