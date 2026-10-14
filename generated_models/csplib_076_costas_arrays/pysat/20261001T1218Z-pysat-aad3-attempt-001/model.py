# Costas array: a permutation of 1..n (one mark per row and column of an n x n grid) in
# which the vectors between all pairs of marks are different. Equivalently, for each
# distance l, the differences costas[i + l] - costas[i] over all i are pairwise different
# (the rows of the difference triangle).
from itertools import combinations

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]

    pool = IDPool()
    # costas[i] = the value (row) of the mark in column i
    costas = [Integer(f"costas{i}", 1, n, vpool=pool) for i in range(n)]
    engine = IntegerEngine(vars=costas, vpool=pool)

    # the marks form a permutation: one per row and one per column
    engine.add_alldifferent(costas)
    cnf = engine.clausify()

    # step[l][i][d] is true when costas[i + l] - costas[i] == d. It is only forced in the
    # direction "the two values are v and v + d, so step is true", which is all the
    # distinctness constraint below needs.
    for l in range(1, n):
        steps_of = {}
        for i in range(n - l):
            for v in range(1, n + 1):
                for w in range(1, n + 1):
                    if v == w:
                        continue
                    step = pool.id(("step", l, i, w - v))
                    cnf.append([-costas[i].equals(v), -costas[i + l].equals(w), step])
                    steps_of.setdefault(w - v, {})[i] = step

        # all differences at distance l are different: no difference d occurs for two start columns
        for d, by_start in steps_of.items():
            for i, j in combinations(sorted(by_start), 2):
                cnf.append([-by_start[i], -by_start[j]])

    return cnf, {"costas": costas}
