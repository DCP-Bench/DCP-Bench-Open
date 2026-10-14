# Bus scheduling: buses start in 4-hour slots and drive for two consecutive slots; every slot
# needs as many buses as its demand, with as few buses in total as possible.
# PySAT only decides satisfiability, so the number of buses is returned as the objective
# (the runner refuses a returned objective instead of ignoring it).
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    demands = instance["demands"]
    slots = len(demands)

    pool = IDPool()
    # x[i] = number of buses that start in slot i
    x = [Integer(f"x{i}", 0, sum(demands), vpool=pool) for i in range(slots)]
    engine = IntegerEngine(vars=x, vpool=pool)

    # the buses that started in slot i and in the slot before cover the demand of slot i+1
    for i in range(slots):
        engine.add_linear(x[i] + x[(i + 1) % slots] >= demands[(i + 1) % slots])

    return engine.clausify(), {"x": x}, ("minimize", sum(x))
