# Fibonacci even: the sum of the even-valued terms of the Fibonacci sequence 1, 2, 3, 5, 8, ...
# that do not exceed four million.
# Probe of the output range with the direct encoding only (one literal per value, no order
# literals): the declared output `res` can only be read from an `Integer` or a literal. The even
# terms below 4,000,000 grow by a factor of about 4.236 each, so their sum is below
# 4,000,000 / (1 - 1/4.236) < 5.3 million.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    pool = IDPool()
    res = Integer("res", 0, 5_300_000, encoding="direct", vpool=pool)
    engine = IntegerEngine(vars=[res], vpool=pool)
    return engine.clausify(), {"res": res}
