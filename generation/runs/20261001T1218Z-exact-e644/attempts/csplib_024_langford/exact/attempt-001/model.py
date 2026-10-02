# Langford's problem: arrange two copies of each number 1..k in a sequence of 2k places so that
# the two copies of i have exactly i numbers between them (they sit i + 1 places apart).
from exact import Exact


def build(instance):
    k = instance["k"]
    length = 2 * k  # two copies of each of the k numbers

    solver = Exact()

    # sol[pos] is the number placed at place pos (1..k)
    sol = [f"sol_{pos}" for pos in range(length)]
    for name in sol:
        solver.addVariable(name, 1, k)

    # first[i][p] = 1 when the first copy of number i sits at place p. The second copy then sits
    # at place p + i + 1, so p can only run up to length - i - 2. Indicators over places are used
    # because Exact has no all-different or element constraint.
    first = {}
    for i in range(1, k + 1):
        for p in range(length - i - 1):
            first[i, p] = f"first_{i}_at_{p}"
            solver.addVariable(first[i, p], 0, 1)

    # each number has exactly one first copy, which fixes where both of its copies are
    for i in range(1, k + 1):
        solver.addConstraint([(1, first[i, p]) for p in range(length - i - 1)], True, 1, True, 1)

    for pos in range(length):
        # the copies of the numbers that cover place pos, either as first copy or as second copy
        covering = []
        for i in range(1, k + 1):
            if (i, pos) in first:
                covering.append((i, first[i, pos]))
            if (i, pos - i - 1) in first:
                covering.append((i, first[i, pos - i - 1]))
        # every place holds exactly one number
        solver.addConstraint([(1, name) for _, name in covering], True, 1, True, 1)
        # the number at place pos is the number i whose copy covers it
        solver.addConstraint(covering + [(-1, sol[pos])], True, 0, True, 0)

    return solver, {"sol": sol}
