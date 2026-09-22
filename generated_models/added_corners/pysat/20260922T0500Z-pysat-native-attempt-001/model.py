# Digits 1..8 around a square, each side cell the sum of its two corners.
# The layout is the puzzle, so the instance carries no fields.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = 8
    pool = IDPool()
    p = [Integer(f"p{i}", 1, n, vpool=pool) for i in range(n)]
    engine = IntegerEngine(vars=p, vpool=pool)
    engine.add_alldifferent(p)

    # reading order: a b c / d e / f g h
    a, b, c, d, e, f, g, h = p
    for target, left, right in ((b, a, c), (d, a, f), (e, c, h), (g, f, h)):
        engine.add_linear(target - left - right == 0)
    return engine.clausify(), {"positions": p}
