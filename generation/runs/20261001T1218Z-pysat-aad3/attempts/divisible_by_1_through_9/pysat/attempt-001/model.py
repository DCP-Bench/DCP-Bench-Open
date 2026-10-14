# Divisible by 1 through 9: find a 10-digit number that uses each digit 0..9 exactly once and
# where the number formed by the first n digits is divisible by n, for n = 1..10.
# Probe of the output range: the declared output `number` is an integer up to 10^10, and the
# runner only reads an `Integer` (finite domain, one literal per value) or a literal.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    pool = IDPool()
    # x[i] = the i-th digit of the number
    x = [Integer(f"x{i}", 0, 9, vpool=pool) for i in range(10)]
    # number = the 10-digit number (the reference bounds it by 10^10). The runner blocks an answer
    # by "number == value", which needs the direct or coupled encoding.
    number = Integer("number", 0, 10 ** 10, encoding="coupled", vpool=pool)
    engine = IntegerEngine(vars=x + [number], vpool=pool)
    engine.add_alldifferent(x)
    return engine.clausify(), {"number": number}
