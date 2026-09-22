# Place n queens so that no two share a row, column or diagonal.
# Columns are 1-indexed, as the reference declares them.
from hermax.model import Model


def build(instance):
    n = instance["n"]

    m = Model()
    queens = m.int_vector("queens", n, 1, n)
    m &= queens.all_different()
    for i in range(n):
        for j in range(i + 1, n):
            m &= (queens[i] - queens[j] != i - j)
            m &= (queens[i] - queens[j] != j - i)
    return m, {"queens": queens}
