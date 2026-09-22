# A four digit PIN abcd with cd = 3*ab and da = 2*bc, all digits distinct.
# The clues are the puzzle, so the instance carries no fields.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    pool = IDPool()
    digits = [Integer(name, 0, 9, vpool=pool) for name in ("a", "b", "c", "d")]
    a, b, c, d = digits
    engine = IntegerEngine(vars=digits, vpool=pool)
    engine.add_alldifferent(digits)

    # 10c + d == 3 * (10a + b)
    engine.add_linear(10 * c + d - 30 * a - 3 * b == 0)
    # 10d + a == 2 * (10b + c)
    engine.add_linear(10 * d + a - 20 * b - 2 * c == 0)
    return engine.clausify(), {"a": a, "b": b, "c": c, "d": d}
