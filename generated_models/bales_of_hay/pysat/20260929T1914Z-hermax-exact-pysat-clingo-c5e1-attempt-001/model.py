# Bales of hay: the bales were weighed in all combinations of two and the
# weights, in numerical order, are given. Find the weight of each bale.
from collections import Counter
from itertools import combinations

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]  # number of bales
    weights = instance["weights"]  # the weights of the pairs, in numerical order
    pairs = list(combinations(range(n), 2))

    pool = IDPool()
    # bales[i] = the weight of bale i
    bales = [Integer(f"bales_{i}", 0, 50, vpool=pool) for i in range(n)]
    # pair_weight[p] = the weight of the p-th pair of bales
    pair_weight = [Integer(f"pair_{i}_{j}", 0, 100, vpool=pool) for i, j in pairs]
    engine = IntegerEngine(vars=bales + pair_weight, vpool=pool)
    for p, (i, j) in enumerate(pairs):
        engine.add_linear(pair_weight[p] == bales[i] + bales[j])
    cnf = engine.clausify()

    # The written-down weights are exactly the weights of the pairs: each weight
    # value is the weight of as many pairs as times it was written down. (There are
    # as many pairs as written weights, so no pair is left over.)
    for value, times in Counter(weights).items():
        cnf.extend(CardEnc.equals(lits=[pair_weight[p].equals(value) for p in range(len(pairs))],
                                  bound=times, vpool=pool, encoding=EncType.seqcounter).clauses)

    return cnf, {"bales": bales}
