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

    # The sums are stated over the value literals "entry = v": a number v in A counts +v, and in B
    # counts -v, so each total is zero exactly when the two sets agree. (The squares are not linear
    # in the entries, but the weights of the value literals can be v * v.)
    entries = [(entry, +1) for entry in A] + [(entry, -1) for entry in B]
    values = range(1, n + 1)
    lits = [entry.equals(v) for entry, _ in entries for v in values]

    # the two sets have the same sum
    sum_weights = [sign * v for _, sign in entries for v in values]
    cnf.extend(PBEnc.equals(lits=lits, weights=sum_weights, bound=0, vpool=pool).clauses)

    # the two sets have the same sum of squares
    square_weights = [sign * v * v for _, sign in entries for v in values]
    cnf.extend(PBEnc.equals(lits=lits, weights=square_weights, bound=0, vpool=pool).clauses)

    return cnf, {"A": A, "B": B}
