# Two disjoint non-empty subsets of A with equal sums.
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.pb import PBEnc


def build(instance):
    a = instance["A"]
    n = len(a)

    pool = IDPool()
    in_s = [pool.id(("s", i)) for i in range(n)]
    in_t = [pool.id(("t", i)) for i in range(n)]
    cnf = CNF()

    # sum(A[i] * in_S[i]) - sum(A[i] * in_T[i]) == 0. PBEnc takes the negative
    # weights directly, so the two halves go in as one constraint.
    cnf.extend(PBEnc.equals(lits=in_s + in_t,
                            weights=list(a) + [-v for v in a], bound=0,
                            vpool=pool).clauses)
    for i in range(n):
        cnf.append([-in_s[i], -in_t[i]])
    cnf.extend(CardEnc.atleast(lits=in_s, bound=1, vpool=pool,
                               encoding=EncType.seqcounter).clauses)
    cnf.extend(CardEnc.atleast(lits=in_t, bound=1, vpool=pool,
                               encoding=EncType.seqcounter).clauses)
    return cnf, {"in_S": in_s, "in_T": in_t}
