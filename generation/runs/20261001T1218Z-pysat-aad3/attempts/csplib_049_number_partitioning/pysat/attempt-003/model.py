# Number partitioning: split the numbers 1..n into two sets A and B of equal size (n / 2 each) with
# the same sum and the same sum of squares. A and B are listed as n / 2 numbers each, in any order.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def build(instance):
    n = instance["n"]  # the numbers are 1..n; n must be even
    half = n // 2

    pool = IDPool()
    # A[i], B[i] = the i-th number listed for the first and the second set
    A = [Integer(f"A{i}", 1, n, vpool=pool) for i in range(half)]
    B = [Integer(f"B{i}", 1, n, vpool=pool) for i in range(half)]
    engine = IntegerEngine(vars=A + B, vpool=pool)

    # the n listed entries are all different, so together they are the numbers 1..n
    engine.add_alldifferent(A + B)
    cnf = engine.clausify()

    # in_A[v] is true when the number v is in A, and false when it is in B. The sums below are
    # stated on these n literals, which keeps the arithmetic small: stating them on the listed
    # entries (n entries with n values each) makes the weighted sums far larger.
    in_A = {v: pool.id(("in_A", v)) for v in range(1, n + 1)}
    for v in range(1, n + 1):
        # v is in A exactly when one of the listed entries of A is v
        cnf.append([-in_A[v]] + [entry.equals(v) for entry in A])
        for entry in A:
            cnf.append([-entry.equals(v), in_A[v]])
        # v is in B exactly when one of the listed entries of B is v
        cnf.append([in_A[v]] + [entry.equals(v) for entry in B])
        for entry in B:
            cnf.append([-entry.equals(v), -in_A[v]])

    # A and B have the same cardinality. This follows from the listings having n / 2 distinct
    # entries each; it is stated because it lets the solver reject unbalanced choices of in_A early.
    cnf.extend(CardEnc.equals(lits=list(in_A.values()), bound=half, vpool=pool,
                              encoding=EncType.seqcounter).clauses)

    # A and B have the same sum, and the same sum of squares: numbers in A count with a plus sign,
    # numbers in B (the numbers not in A) with a minus sign, and each total must be zero
    lits = [in_A[v] for v in range(1, n + 1)] + [-in_A[v] for v in range(1, n + 1)]
    cnf.extend(PBEnc.equals(lits=lits, weights=[v for v in range(1, n + 1)] + [-v for v in range(1, n + 1)],
                            bound=0, vpool=pool).clauses)
    cnf.extend(PBEnc.equals(lits=lits, weights=[v * v for v in range(1, n + 1)] + [-v * v for v in range(1, n + 1)],
                            bound=0, vpool=pool).clauses)

    return cnf, {"A": A, "B": B}
