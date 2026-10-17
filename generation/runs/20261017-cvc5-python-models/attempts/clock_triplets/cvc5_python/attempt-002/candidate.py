# Clock triplets: rearrange the numbers 1 to 12 on the face of a clock so that
# no triplet of adjacent numbers has a sum higher than 21.
# Output x: the arrangement of the numbers on the clock, as 12 integers.
#
# Encoding: a Boolean matrix b[i][v] says that position i holds the number v.
# Each position holds exactly one number, and each number sits in exactly one
# position. The output x[i] is the number at position i. The triplet bound is
# written as forbidden combinations of values, so the search is propositional.
import cvc5.pythonic as cz

N = 12
MAX_TRIPLET_SUM = 21
VALUES = range(1, N + 1)


def build(instance):
    b = [[cz.Bool(f"b_{i}_{v}") for v in VALUES] for i in range(N)]
    constraints = []

    # Rearrange the numbers 1 to 12 on the face of the clock: each position holds
    # exactly one number.
    for i in range(N):
        constraints.append(cz.Or([b[i][v - 1] for v in VALUES]))
        for v in VALUES:
            for w in VALUES:
                if v < w:
                    constraints.append(cz.Not(cz.And(b[i][v - 1], b[i][w - 1])))

    # Every number from 1 to 12 is used exactly once on the clock face.
    for v in VALUES:
        constraints.append(cz.Or([b[i][v - 1] for i in range(N)]))
        for i in range(N):
            for j in range(i + 1, N):
                constraints.append(cz.Not(cz.And(b[i][v - 1], b[j][v - 1])))

    # No triplet of adjacent numbers has a sum higher than 21. The clock is a circle,
    # so the triplets wrap around from the last position back to the first. Each
    # forbidden combination of three values at three adjacent positions is excluded.
    for i in range(N):
        p, q, r = i, (i + 1) % N, (i + 2) % N
        for a in VALUES:
            for c in VALUES:
                for d in VALUES:
                    if a + c + d > MAX_TRIPLET_SUM:
                        constraints.append(
                            cz.Not(cz.And(b[p][a - 1], b[q][c - 1], b[r][d - 1]))
                        )

    # The output is the number at each position.
    x = [cz.Sum([cz.If(b[i][v - 1], v, 0) for v in VALUES]) for i in range(N)]
    return constraints, {"x": x}
