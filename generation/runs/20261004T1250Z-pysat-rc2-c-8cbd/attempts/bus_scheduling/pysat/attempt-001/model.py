# Bus scheduling (Taha): choose how many buses start work in each 4-hour slot
# of a cyclic day so that every slot's demand is covered, each bus working
# two consecutive slots, using as few buses as possible.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def build(instance):
    demands = instance["demands"]
    slots = len(demands)

    pool = IDPool()
    # x[i] is the number of buses starting in slot i. The reference allows up
    # to sum(demands); an optimal schedule never starts more than the largest
    # demand in one slot (any excess over the demand of the two slots the
    # buses cover could be removed at a saving), so that is the upper bound
    # (at least 1 so the domain is never a single value). The domains are
    # small, so the direct encoding is cheap and gives the value literals the
    # objective is written with.
    top = max(max(demands), 1)
    x = [Integer(f"x_{i}", 0, top, vpool=pool) for i in range(slots)]
    engine = IntegerEngine(vars=x, vpool=pool)

    # The buses starting in slot i and in slot i+1 (cyclically) are the ones
    # at work in slot i+1, and they must meet that slot's demand.
    for i in range(slots):
        engine.add_linear(x[i] + x[(i + 1) % slots] >= demands[(i + 1) % slots])

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # Minimise the total number of buses: starting v buses in a slot pays v.
    for i in range(slots):
        for v in range(1, top + 1):
            formula.append([-x[i].equals(v)], weight=v)

    return formula, {"x": x}
