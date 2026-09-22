# Place n queens so that no two share a row, column or diagonal.
# Columns are 1-indexed, as the reference declares them.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]

    pool = IDPool()
    queens = [Integer(f"q{i}", 1, n, vpool=pool) for i in range(n)]
    engine = IntegerEngine(vars=queens, vpool=pool)
    engine.add_alldifferent(queens)
    # The two diagonals, as linear disequalities rather than value pairs.
    for i in range(n):
        for j in range(i + 1, n):
            engine.add_linear(queens[i] - queens[j] != i - j)
            engine.add_linear(queens[i] - queens[j] != j - i)
    return engine.clausify(), {"queens": queens}
