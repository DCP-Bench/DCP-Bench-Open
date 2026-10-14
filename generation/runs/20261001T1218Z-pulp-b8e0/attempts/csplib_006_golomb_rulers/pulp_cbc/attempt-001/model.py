"""Golomb ruler: place `size` marks at integer positions 0 = a_1 < a_2 < ... < a_m so
that the m(m-1)/2 differences a_j - a_i (i < j) are all distinct, and the length
a_m of the ruler is as small as possible.

The model reports the positions of the marks and the length of the ruler.
"""
import pulp


def build(instance):
    size = instance["size"]  # number of marks
    # The reference lets every mark lie between 0 and size * size; the model keeps
    # that range, so positions 0..horizon are the only places a mark can go.
    horizon = size * size

    problem = pulp.LpProblem("golomb_ruler", pulp.LpMinimize)

    # Mark k (k = 0..size-1) is preceded by k marks and followed by size-1-k, all at
    # distinct positions, so it lies between k and horizon - (size - 1 - k). The
    # first mark is at 0.
    first = list(range(size))
    last = [0 if k == 0 else horizon - (size - 1 - k) for k in range(size)]

    # at[k][p] = 1 if mark k is at position p
    at = [{p: pulp.LpVariable(f"at_{k}_{p}", cat="Binary") for p in range(first[k], last[k] + 1)}
          for k in range(size)]

    # marks[k] = position of mark k (declared output), a bounded integer tied to
    # the 0/1 variables by equality; length = position of the last mark (declared output)
    marks = [pulp.LpVariable(f"marks_{k}", first[k], last[k], cat="Integer") for k in range(size)]
    length = marks[size - 1]

    # objective: minimise the length of the ruler
    problem += length

    # every mark is at exactly one position, and marks reads it back
    for k in range(size):
        problem += pulp.lpSum(at[k].values()) == 1
        problem += marks[k] == pulp.lpSum(p * var for p, var in at[k].items())

    # the first mark is at 0, and the marks are increasing along the ruler
    problem += marks[0] == 0
    for k in range(size - 1):
        problem += marks[k] + 1 <= marks[k + 1]

    # occupied[p] = 1 if some mark is at position p (a position holds at most one mark,
    # because the marks are strictly increasing)
    occupied = []
    for p in range(horizon + 1):
        var = pulp.LpVariable(f"occupied_{p}", cat="Binary")
        problem += var == pulp.lpSum(at[k][p] for k in range(size) if p in at[k])
        occupied.append(var)

    # all differences are distinct: for each distance d, at most one pair of
    # marks lies exactly d apart. pair[d][p] is forced to 1 when positions p and
    # p + d are both occupied, and the pairs at one distance add up to at most 1.
    for d in range(1, horizon + 1):
        pair = []
        for p in range(horizon - d + 1):
            both = pulp.LpVariable(f"pair_{d}_{p}", 0, 1)
            problem += both >= occupied[p] + occupied[p + d] - 1
            pair.append(both)
        problem += pulp.lpSum(pair) <= 1

    # Implied bound that tightens the relaxation: the size*(size-1)/2 differences are
    # distinct positive integers no larger than the length, so the length is at
    # least size*(size-1)/2.
    problem += length >= size * (size - 1) // 2

    return problem, {"marks": marks, "length": length}
