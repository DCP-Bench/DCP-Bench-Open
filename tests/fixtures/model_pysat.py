from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]
    pool = IDPool()
    x = Integer("x", 0, n, vpool=pool)
    y = Integer("y", 0, n, vpool=pool)
    engine = IntegerEngine(vars=[x, y], vpool=pool)
    engine.add_linear(x + y == n)
    return engine.clausify(), {"x": x, "y": y}
