# Who killed Aunt Agatha in Dreadsbury Mansion: the killer is one of Agatha, the
# butler and Charles, hates the victim and is no richer than the victim.
# People are indexed as in the instance: 0 Agatha, 1 the butler, 2 Charles.
from pyscipopt import Model, quicksum

AGATHA, BUTLER, CHARLES = 0, 1, 2


def build(instance):
    names = instance["names"]
    n = len(names)
    people = range(n)

    m = Model()
    # hates[i, j] = 1 if person i hates person j
    hates = {(i, j): m.addVar(name=f"hates_{i}_{j}", vtype="B") for i in people for j in people}
    # wealth[i] = relative wealth of person i; only the order matters, so n levels suffice
    wealth = [m.addVar(name=f"wealth_{i}", vtype="I", lb=0, ub=n) for i in people]
    # richer[j] = 1 if person j is richer than Agatha
    richer = {j: m.addVar(name=f"richer_{j}", vtype="B") for j in people}
    # killed[i] = 1 if person i killed Agatha (exactly one killer)
    killed = [m.addVar(name=f"killed_{i}", vtype="B") for i in people]

    # wealth ordering that defines richer[j]
    for j in people:
        m.addConsIndicator(wealth[j] - wealth[AGATHA] >= 1, binvar=richer[j])
        m.addConsIndicator(wealth[j] - wealth[AGATHA] <= 0, binvar=richer[j], activeone=False)

    # someone in the mansion killed Agatha
    m.addCons(quicksum(killed) == 1)

    # a killer always hates his victim, and is no richer than the victim
    for i in people:
        m.addCons(killed[i] <= hates[i, AGATHA])
        m.addConsIndicator(wealth[i] - wealth[AGATHA] <= 0, binvar=killed[i])

    # Agatha hates everybody except the butler
    for j in people:
        m.addCons(hates[AGATHA, j] == (1 if j != BUTLER else 0))

    # the butler hates everyone not richer than Agatha, and everyone whom Agatha hates
    for j in people:
        m.addCons(hates[BUTLER, j] == 1 - richer[j])
        m.addCons(hates[BUTLER, j] >= hates[AGATHA, j])

    # Charles hates noone that Agatha hates
    for j in people:
        m.addCons(hates[CHARLES, j] + hates[AGATHA, j] <= 1)

    # noone hates everyone
    for i in people:
        m.addCons(quicksum(hates[i, j] for j in people) <= n - 1)

    # the output is the 0-based index of the killer
    killer = quicksum(i * killed[i] for i in people)
    return m, {"killer": killer}
