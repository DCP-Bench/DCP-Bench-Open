# 12-pack problem: buy packs of the given sizes so that the total number of
# items reaches the target, with the total as small as possible.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def build(instance):
    target = instance["target"]
    packs = instance["packs"]
    n = len(packs)
    max_val = target * 2  # the reference's bound on every count

    pool = IDPool()
    # Buying ceil(target / p) packs of the smallest size p reaches the target
    # with fewer than target + p items, so no minimal total is larger than
    # target + p - 1. The total is given that range (its lower end is the
    # constraint total >= target), which leaves every minimal answer in place
    # and keeps the encodings small. Pack sizes are positive by the problem.
    smallest = min(packs)
    high = target + smallest - 1
    # total, target..high. Order encoding: the objective pays one per
    # threshold above the target.
    total = Integer("total", target, high, encoding="order", vpool=pool)
    # counts[i], 0..min(max_val, high // packs[i]): no more packs of size
    # packs[i] than fit in the largest total. Coupled encoding: thresholds
    # for the sum, value literals for the runner to block a reported answer.
    counts = [Integer(f"counts_{i}", 0, min(max_val, high // packs[i]),
                      encoding="coupled", vpool=pool) for i in range(n)]
    engine = IntegerEngine(vars=counts + [total], vpool=pool)

    # The total number of items is the sum of pack sizes times pack counts.
    engine.add_linear(sum(packs[i] * counts[i] for i in range(n)) - total == 0)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # Minimise the total: each item above the target pays 1, which differs
    # from the total by the constant target.
    for v in range(target + 1, high + 1):
        formula.append([-total.ge(v)], weight=1)

    return formula, {"counts": counts}
