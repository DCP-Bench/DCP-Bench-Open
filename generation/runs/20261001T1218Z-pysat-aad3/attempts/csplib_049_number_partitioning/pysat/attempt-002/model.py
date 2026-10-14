# Number partitioning: split the numbers 1..n into two sets A and B of equal size (n / 2 each) with
# the same sum and the same sum of squares. A and B are listed as n / 2 numbers each.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def build(instance):
    n = instance["n"]  # the numbers are 1..n; n must be even
    half = n // 2

    pool = IDPool()
    # A[i], B[i] = the i-th number of the first and the second set
    A = [Integer(f"A{i}", 1, n, vpool=pool) for i in range(half)]
    B = [Integer(f"B{i}", 1, n, vpool=pool) for i in range(half)]
    engine = IntegerEngine(vars=A + B, vpool=pool)

    # the n entries of both sets are all different, so together they are the numbers 1..n
    engine.add_alldifferent(A + B)
    cnf = engine.clausify()

    # A and B are sets, so each is listed in increasing order, and the sets are interchangeable, so A is
    # the one that contains 1. This fixes one listing for each partition instead of
    # (n/2)! * (n/2)! * 2, which a search for sums and squares otherwise has to wade through.
    for entries in (A, B):
        for i in range(half - 1):
            for v in range(1, n + 1):
                for u in range(v, n + 1):
                    cnf.append([-entries[i + 1].equals(v), -entries[i].equals(u)])
    cnf.append([A[0].equals(1)])

    # in_A[v] is true when the number v is in A (and then it is not in B, since all entries differ)
    in_A = {v: pool.id(("in_A", v)) for v in range(1, n + 1)}
    for v in range(1, n + 1):
        cnf.append([-in_A[v]] + [entry.equals(v) for entry in A])
        for entry in A:
            cnf.append([-entry.equals(v), in_A[v]])

    # A and B have the same sum, and the same sum of squares: numbers in A count with a plus sign,
    # numbers in B (the numbers not in A) with a minus sign, and each total must be zero
    lits = [in_A[v] for v in range(1, n + 1)] + [-in_A[v] for v in range(1, n + 1)]
    cnf.extend(PBEnc.equals(lits=lits, weights=[v for v in range(1, n + 1)] + [-v for v in range(1, n + 1)],
                            bound=0, vpool=pool).clauses)
    cnf.extend(PBEnc.equals(lits=lits, weights=[v * v for v in range(1, n + 1)] + [-v * v for v in range(1, n + 1)],
                            bound=0, vpool=pool).clauses)

    return cnf, {"A": A, "B": B}
