# Ternary Steiner system of order n: find n*(n-1)/6 triples of the elements
# 1..n such that any two triples have at most one element in common (n must be
# 1 or 3 modulo 6).
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool


def build(instance):
    n = instance["n"]  # number of elements
    n_sets = n * (n - 1) // 6  # number of triples

    pool = IDPool()
    # sets[i][j] is true when element j belongs to triple i
    sets = [[pool.id(("sets", i, j)) for j in range(n)] for i in range(n_sets)]

    cnf = CNF()
    # every triple has exactly three elements
    for i in range(n_sets):
        cnf.extend(CardEnc.equals(lits=sets[i], bound=3, vpool=pool, encoding=EncType.seqcounter).clauses)

    # Two triples share at most one element exactly when no pair of elements lies
    # in two triples. For each pair of elements, together[i] is forced true when
    # triple i holds both, and at most one triple may.
    for p in range(n):
        for q in range(p + 1, n):
            together = [pool.id(("together", p, q, i)) for i in range(n_sets)]
            for i in range(n_sets):
                cnf.append([-sets[i][p], -sets[i][q], together[i]])
            cnf.extend(CardEnc.atmost(lits=together, bound=1, vpool=pool, encoding=EncType.seqcounter).clauses)

    return cnf, {"sets": sets}
