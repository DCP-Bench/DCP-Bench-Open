# Who killed Agatha (Dreadsbury Mansion): Agatha, the butler and Charles live in the mansion and one
# of them killed Agatha. From who hates whom and who is richer than whom, find the killer.
from pychoco.model import Model

# The roles of the three residents (Agatha 0, the butler 1, Charles 2) are part of the puzzle
# statement; the instance gives their names.
AGATHA, BUTLER, CHARLES = 0, 1, 2


def build(instance):
    n = len(instance["names"])  # the residents, the only people in the mansion
    victim = AGATHA
    people = range(n)

    model = Model()

    killer = model.intvar(0, n - 1, name="killer")
    # hates[i][j]: i hates j; richer[i][j]: i is richer than j
    hates = [[model.boolvar(name=f"hates_{i}_{j}") for j in people] for i in people]
    richer = [[model.boolvar(name=f"richer_{i}_{j}") for j in people] for i in people]
    true = model.intvar(1, 1, name="true")
    false = model.intvar(0, 0, name="false")

    # A killer always hates his victim, and is no richer than his victim.
    model.element(true, [hates[i][victim] for i in people], killer).post()
    model.element(false, [richer[i][victim] for i in people], killer).post()

    # Richness: nobody is richer than himself, and of two different people exactly one is richer.
    for i in people:
        model.arithm(richer[i][i], "=", 0).post()
        for j in range(i + 1, n):
            model.arithm(richer[i][j], "+", richer[j][i], "=", 1).post()

    # Charles hates no one that Agatha hates.
    for i in people:
        model.arithm(hates[AGATHA][i], "+", hates[CHARLES][i], "<=", 1).post()

    # Agatha hates everybody except the butler.
    for i in people:
        model.arithm(hates[AGATHA][i], "=", 0 if i == BUTLER else 1).post()

    # The butler hates everyone not richer than Aunt Agatha.
    for i in people:
        model.arithm(richer[i][AGATHA], "+", hates[BUTLER][i], ">=", 1).post()

    # The butler hates everyone whom Agatha hates.
    for i in people:
        model.arithm(hates[AGATHA][i], "<=", hates[BUTLER][i]).post()

    # No one hates everyone.
    for i in people:
        model.sum(hates[i], "<=", n - 1).post()

    return model, {"killer": killer}
