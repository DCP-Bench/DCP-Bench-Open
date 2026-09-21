# Place n queens so that no two share a row, column or diagonal.
# Columns are 1-indexed, as the reference declares them.
from dcp_pb import Pb


def build(instance):
    n = instance["n"]

    pb = Pb()
    queens = pb.ints(n, 1, n)
    pb.all_different(queens)
    # The two diagonal all-differents, through the same indicators.
    for i in range(n):
        for j in range(i + 1, n):
            for v in range(1, n + 1):
                here = pb.is_value(queens[i], v)
                for w in (v + (j - i), v - (j - i)):
                    if 1 <= w <= n:
                        pb.at_most([here, pb.is_value(queens[j], w)], 1)
    return pb, {"queens": queens}
