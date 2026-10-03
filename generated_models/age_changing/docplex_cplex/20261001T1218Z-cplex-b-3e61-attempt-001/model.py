"""Age changing (Enigma 1224): applying the four operations +2, /8, -3 and *7 in some order to my
age gives my husband's age, and applying the same four operations in a different order to his
age gives mine. What are our two ages?

The model reports my age and my husband's age. The puzzle has no instance data; the operations,
the age range 16..120 and the bound 1..1000 on intermediate values are the reference's own.
"""
from docplex.mp.model import Model


def build(instance):
    n = 4                          # number of operations (puzzle constant)
    age_low, age_high = 16, 120    # ages considered (reference bounds)
    low, high = 1, 1000            # intermediate values (reference bounds)
    ops = range(n)                 # 0: +2, 1: /8, 2: -3, 3: *7
    steps = range(n)

    model = Model("age_changing")

    m = model.integer_var(age_low, age_high, name="m")  # my age
    h = model.integer_var(age_low, age_high, name="h")  # my husband's age

    # Values after each operation, starting from my age (hlist) and from his age (mlist).
    hlist = [model.integer_var(low, high, name=f"hlist_{i}") for i in range(n + 1)]
    mlist = [model.integer_var(low, high, name=f"mlist_{i}") for i in range(n + 1)]

    # order1[i, k] = 1 when operation k is applied at step i to my age; order2 likewise to his
    # age. Each is a permutation: every step applies one operation and every operation is used.
    order1 = {(i, k): model.binary_var(name=f"order1_{i}_{k}") for i in steps for k in ops}
    order2 = {(i, k): model.binary_var(name=f"order2_{i}_{k}") for i in steps for k in ops}
    for order in (order1, order2):
        for i in steps:
            model.add_constraint(model.sum(order[i, k] for k in ops) == 1)
        for k in ops:
            model.add_constraint(model.sum(order[i, k] for i in steps) == 1)

    # The two orders differ: at most n - 1 steps apply the same operation in both. same[i, k]
    # is at least 1 when both orders apply operation k at step i.
    same = {(i, k): model.binary_var(name=f"same_{i}_{k}") for i in steps for k in ops}
    for i in steps:
        for k in ops:
            model.add_constraint(same[i, k] >= order1[i, k] + order2[i, k] - 1)
    model.add_constraint(model.sum(same.values()) <= n - 1)

    # Starting from my age, the operations give my husband's age.
    model.add_constraint(hlist[0] == m)
    model.add_constraint(hlist[n] == h)

    # Starting from his age, the operations in the other order give my age.
    model.add_constraint(mlist[0] == h)
    model.add_constraint(mlist[n] == m)

    # Each step applies its operation: +2, /8 (as 8 * new == old, so only exact divisions),
    # -3, or *7.
    for order, vals in ((order1, hlist), (order2, mlist)):
        for i in steps:
            old, new = vals[i], vals[i + 1]
            model.add_indicator(order[i, 0], new == old + 2)
            model.add_indicator(order[i, 1], 8 * new == old)
            model.add_indicator(order[i, 2], new == old - 3)
            model.add_indicator(order[i, 3], new == 7 * old)

    return model, {"m": m, "h": h}
