# Eighteen holes of par 3, 4 or 5 adding up to a par-72 course.
# The course specification is the puzzle, so the instance carries no fields.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    pool = IDPool()
    holes = [Integer(f"hole{i}", 3, 5, vpool=pool) for i in range(18)]
    engine = IntegerEngine(vars=holes, vpool=pool)
    engine.add_linear(sum(holes) == 72)
    return engine.clausify(), {"holes": holes}
