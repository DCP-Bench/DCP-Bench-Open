# Knapsack: choose items to carry, maximising their total value without the
# total weight exceeding the backpack's capacity.
from pysat.formula import IDPool, WCNF
from pysat.pb import PBEnc


def build(instance):
    values = instance["values"]
    weights = instance["weights"]
    capacity = instance["capacity"]
    n = len(values)

    pool = IDPool()
    # take[i] is true when item i goes into the backpack.
    take = [pool.id(("take", i)) for i in range(n)]

    formula = WCNF()
    # The items taken must not weigh more than the capacity (hard clauses).
    formula.extend(PBEnc.leq(lits=take, weights=weights, bound=capacity,
                             vpool=pool).clauses)

    # Maximise the value carried: leaving item i behind pays its value, so the
    # weight RC2 minimises is the value left out, which is the shortfall from
    # the total value of all items.
    for i in range(n):
        if values[i] > 0:
            formula.append([take[i]], weight=values[i])

    return formula, {"x": take}
