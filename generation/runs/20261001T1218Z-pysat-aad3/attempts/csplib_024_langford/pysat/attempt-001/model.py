# Langford's problem: arrange two copies of each of the numbers 1..k in a sequence of
# length 2k so that the two copies of the number i have exactly i numbers between them
# (their positions differ by i + 1).
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    k = instance["k"]

    pool = IDPool()
    # sol[p] = the number at position p of the sequence (positions 0..2k-1)
    sol = [Integer(f"sol{p}", 1, k, vpool=pool) for p in range(2 * k)]
    engine = IntegerEngine(vars=sol, vpool=pool)
    cnf = engine.clausify()

    # first[i][p] is true when the first copy of i is at position p; its second copy is then at
    # position p + i + 1, so p can only go up to 2k - i - 2
    first = {i: [pool.id(("first", i, p)) for p in range(2 * k - i - 1)] for i in range(1, k + 1)}

    # each number i has its first copy at exactly one position
    for i in range(1, k + 1):
        cnf.extend(CardEnc.equals(lits=first[i], bound=1, vpool=pool, encoding=EncType.seqcounter).clauses)

    # the two copies of i are i + 1 apart: placing the first copy at p puts the number i at
    # both p and p + i + 1. Each position holds one number (the integer takes one value), so
    # two numbers cannot share a position; 2k copies fill the 2k positions exactly.
    for i in range(1, k + 1):
        for p, placed in enumerate(first[i]):
            cnf.append([-placed, sol[p].equals(i)])
            cnf.append([-placed, sol[p + i + 1].equals(i)])

    return cnf, {"sol": sol}
