from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]
    pool = IDPool()
    x = Integer("x", 0, n, vpool=pool)
    y = Integer("y", 0, n, vpool=pool)
    engine = IntegerEngine(vars=[x, y], vpool=pool)
    if not instance["optimize"]:
        engine.add_linear(x + y == n)
        return engine.clausify(), {"x": x, "y": y}
    engine.add_linear(x + y >= n)
    # The objective as soft clauses: an assignment pays `cost` whenever x or y
    # takes the value v, so the total paid is x + y.
    formula = WCNF()
    formula.extend(engine.clausify().clauses)
    for v, cost in ((v, v) for v in range(n + 1)):
        if cost > 0:
            formula.append([-x.equals(v)], weight=cost)
            formula.append([-y.equals(v)], weight=cost)
    return formula, {"x": x, "y": y}
