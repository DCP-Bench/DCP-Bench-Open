# Who killed Agatha: Agatha, the butler and Charles live in Dreadsbury Mansion and are the only
# ones there. Agatha was killed by one of them; hate and wealth relations between the three
# decide who the killer was. The model returns the killer's 0-based index.
from exact import Exact


def build(instance):
    n = len(instance["names"])  # the residents of the mansion
    agatha, butler, charles = 0, 1, 2  # their positions in `names`, as in the problem statement
    victim = agatha

    solver = Exact()

    # hates[i][j] = 1 when i hates j;  richer[i][j] = 1 when i is richer than j
    hates = [[f"hates_{i}_{j}" for j in range(n)] for i in range(n)]
    richer = [[f"richer_{i}_{j}" for j in range(n)] for i in range(n)]
    for matrix in (hates, richer):
        for row in matrix:
            for name in row:
                solver.addVariable(name, 0, 1)

    # killer is 0 = Agatha, 1 = the butler, 2 = Charles. Whom the killer is decides which rows of
    # hates and richer the killer rule applies to, so it is spelled out with one 0/1 indicator
    # per person: is_killer[i] = 1 when killer == i.
    solver.addVariable("killer", 0, n - 1)
    is_killer = [f"is_killer_{i}" for i in range(n)]
    for name in is_killer:
        solver.addVariable(name, 0, 1)
    solver.addConstraint([(1, name) for name in is_killer], True, 1, True, 1)
    solver.addConstraint([(i, is_killer[i]) for i in range(1, n)] + [(-1, "killer")],
                         True, 0, True, 0)

    # A killer always hates, and is no richer than, his victim.
    for i in range(n):
        # is_killer[i] -> hates[i][victim]
        solver.addConstraint([(1, hates[i][victim]), (-1, is_killer[i])], True, 0)
        # is_killer[i] -> not richer[i][victim]
        solver.addConstraint([(1, richer[i][victim]), (1, is_killer[i])], False, 0, True, 1)

    # Wealth is a strict order: nobody is richer than himself, and of two different people exactly
    # one is richer than the other.
    for i in range(n):
        solver.addConstraint([(1, richer[i][i])], True, 0, True, 0)
    for i in range(n):
        for j in range(i + 1, n):
            solver.addConstraint([(1, richer[i][j]), (1, richer[j][i])], True, 1, True, 1)

    # Charles hates no one that Agatha hates:  hates[agatha][i] -> not hates[charles][i]
    for i in range(n):
        solver.addConstraint([(1, hates[agatha][i]), (1, hates[charles][i])], False, 0, True, 1)

    # Agatha hates everybody except the butler.
    for i in range(n):
        value = 0 if i == butler else 1
        solver.addConstraint([(1, hates[agatha][i])], True, value, True, value)

    # The butler hates everyone not richer than Aunt Agatha:  not richer[i][agatha] -> hates[butler][i]
    for i in range(n):
        solver.addConstraint([(1, richer[i][agatha]), (1, hates[butler][i])], True, 1)

    # The butler hates everyone whom Agatha hates:  hates[agatha][i] -> hates[butler][i]
    for i in range(n):
        solver.addConstraint([(1, hates[butler][i]), (-1, hates[agatha][i])], True, 0)

    # No one hates everyone: each person hates at most n - 1 of the residents.
    for i in range(n):
        solver.addConstraint([(1, hates[i][j]) for j in range(n)], False, 0, True, n - 1)

    return solver, {"killer": "killer"}
