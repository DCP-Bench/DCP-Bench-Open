"""Minimum-cost vertex cover: every edge needs an endpoint chosen, and the cost is minimised."""
from itertools import combinations

from pysat.examples.rc2 import RC2Stratified
from pysat.formula import IDPool, WCNF

VERTICES = range(6)
COST = [4, 3, 2, 5, 1, 6]
EDGES = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0), (1, 4)]

pool = IDPool()
take = {v: pool.id(("take", v)) for v in VERTICES}

wcnf = WCNF()
for u, v in EDGES:
    wcnf.append([take[u], take[v]])            # hard: every edge is covered
for v in VERTICES:
    wcnf.append([-take[v]], weight=COST[v])    # soft: pay the cost of each vertex taken

rc2 = RC2Stratified(wcnf, solver="glucose42")
model = rc2.compute()
true_lits = {lit for lit in model if lit > 0}
cover = [v for v in VERTICES if take[v] in true_lits]
print("Minimum cost:", rc2.cost)
print("Cover:", cover)
print("Covers every edge:", all(u in cover or v in cover for u, v in EDGES))

brute = min(sum(COST[v] for v in s) for k in range(len(VERTICES) + 1)
            for s in combinations(VERTICES, k)
            if all(u in s or v in s for u, v in EDGES))
print("Matches brute force:", rc2.cost == brute)
rc2.delete()
