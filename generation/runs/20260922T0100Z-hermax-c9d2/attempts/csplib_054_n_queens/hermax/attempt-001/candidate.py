# Place n queens so that no two share a row, column or diagonal.
# Columns are 1-indexed, as the reference declares them.
from dcp_maxsat import MaxSat


def build(instance):
    n = instance["n"]

    sat = MaxSat()
    queens = sat.ints(n, 1, n)
    sat.all_different(queens)
    for i in range(n):
        for j in range(i + 1, n):
            for v in range(1, n + 1):
                here = queens[i].literal(v)
                for w in (v + (j - i), v - (j - i)):
                    there = queens[j].literal(w)
                    if there is not None:
                        sat.clause([-here, -there])
    return sat, {"queens": queens}
