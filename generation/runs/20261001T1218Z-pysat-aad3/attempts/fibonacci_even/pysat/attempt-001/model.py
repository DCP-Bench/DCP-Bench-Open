# Fibonacci even: the sum of the even-valued terms of the Fibonacci sequence 1, 2, 3, 5, 8, ...
# that do not exceed four million.
# Probe of the output range: the declared output `res` is an integer that can only be read from an
# `Integer` (finite domain, one literal per value) or a literal. The even terms below 4,000,000
# grow by a factor of about 4.236 each, so their sum is below 4,000,000 / (1 - 1/4.236) < 5.3 million.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    pool = IDPool()
    # res = the sum; the runner blocks an answer by "res == value", which needs the direct or
    # coupled encoding.
    res = Integer("res", 0, 5_300_000, encoding="coupled", vpool=pool)
    engine = IntegerEngine(vars=[res], vpool=pool)
    return engine.clausify(), {"res": res}
