# Clock triplets: arrange the numbers 1 to 12 on a clock face so that no three
# neighbouring numbers add up to more than 21.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    n = 12
    pool = IDPool()
    # x[i] = the number at position i of the clock
    x = [Integer(f"x_{i}", 1, n, vpool=pool) for i in range(n)]
    engine = IntegerEngine(vars=x, vpool=pool)

    # every number appears once
    engine.add_alldifferent(x)

    # no three neighbouring positions (going round the clock) add up to more than 21
    for i in range(n):
        engine.add_linear(x[i] + x[(i + 1) % n] + x[(i + 2) % n] <= 21)

    return engine.clausify(), {"x": x}
