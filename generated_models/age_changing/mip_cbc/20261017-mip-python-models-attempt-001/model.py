# Age changing: my age m and my husband's age h are non-negative integers.
# Applying the four operations +2, /8, -3, *7, each once and in some order, to
# my age gives his age; applying the same four in a different order to his age
# gives mine. Declared outputs: m (my age) and h (his age).
import itertools

import mip

# Domain bound for both ages. The description gives no bound; 150 is a human age
# limit and is only used to make the big-M constants finite.
AGE_MAX = 150
# Intermediate values: the largest is 7 times (age + 2), since +2 may come before *7.
VAL_MAX = 7 * (AGE_MAX + 2)
# Big-M: larger than any gap between the two sides of one operation step.
BIG_M = 8 * VAL_MAX + 3

# The four operations, as (kind, constant). Index i of an order refers to OPS[i].
OPS = [("add", 2), ("div", 8), ("sub", 3), ("mul", 7)]
# All 24 orders of the four operations.
ORDERS = list(itertools.permutations(range(len(OPS))))


def add_chain(model, start, end, prefix):
    # One chain from start to end: exactly one order of the four operations
    # is chosen by a binary, and that order must take start to end.
    # Operation steps linking the values along the chosen order.
    chosen = {}
    for k, order in enumerate(ORDERS):
        b = model.add_var(name=f"{prefix}_order_{k}", var_type=mip.BINARY)
        chosen[order] = b
        values = [start]
        for i in range(len(OPS) - 1):
            values.append(
                model.add_var(name=f"{prefix}_{k}_v{i + 1}", lb=0, ub=VAL_MAX,
                              var_type=mip.INTEGER))
        values.append(end)
        for step, op_index in enumerate(order):
            kind, c = OPS[op_index]
            x, y = values[step], values[step + 1]
            # each step is an equation lhs == rhs, active only when b = 1
            if kind == "add":  # the next value is the current plus c
                lhs, rhs = y, x + c
            elif kind == "sub":  # the next value is the current minus c
                lhs, rhs = y, x - c
            elif kind == "mul":  # the next value is c times the current
                lhs, rhs = y, c * x
            else:  # "div": the current value is c times the next, so c divides it exactly
                lhs, rhs = x, c * y
            model.add_constr(lhs - rhs <= BIG_M * (1 - b))
            model.add_constr(rhs - lhs <= BIG_M * (1 - b))
    # exactly one order is used for this chain
    model.add_constr(mip.xsum(chosen.values()) == 1)
    return chosen


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    m = model.add_var(name="m", lb=0, ub=AGE_MAX, var_type=mip.INTEGER)
    h = model.add_var(name="h", lb=0, ub=AGE_MAX, var_type=mip.INTEGER)

    # Starting from my age and applying the four operations in some order gives
    # my husband's age.
    from_me = add_chain(model, m, h, "me_to_husband")
    # Starting from his age and applying the same four operations in a different
    # order gives my age.
    from_him = add_chain(model, h, m, "husband_to_me")

    # the two orders must be different: no order is used by both chains
    for order in ORDERS:
        model.add_constr(from_me[order] + from_him[order] <= 1)

    return model, {"h": h, "m": m}
