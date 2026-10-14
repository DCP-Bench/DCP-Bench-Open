"""Who killed Agatha (Dreadsbury Mansion): Agatha, the butler and Charles are the only
people in the mansion, and one of them killed Agatha. From the facts about who hates whom
and who is richer than whom, find the killer.

The model reports the 0-based index of the killer (0 Agatha, 1 the butler, 2 Charles).
"""
import pulp


def build(instance):
    names = instance["names"]  # the residents; the puzzle's facts name the first three
    n = len(names)
    people = range(n)
    agatha, butler, charles = 0, 1, 2
    victim = agatha

    problem = pulp.LpProblem("who_killed_agatha", pulp.LpMinimize)  # satisfaction

    # is_killer[k] = 1 if person k is the killer; exactly one is
    is_killer = [pulp.LpVariable(f"is_killer_{k}", cat="Binary") for k in people]
    problem += pulp.lpSum(is_killer) == 1
    killer = pulp.lpSum(k * var for k, var in enumerate(is_killer))

    # hates[i][j] = 1 if i hates j; richer[i][j] = 1 if i is richer than j
    hates = [[pulp.LpVariable(f"hates_{i}_{j}", cat="Binary") for j in people] for i in people]
    richer = [[pulp.LpVariable(f"richer_{i}_{j}", cat="Binary") for j in people] for i in people]

    # A killer always hates, and is no richer than, his victim.
    for k in people:
        problem += hates[k][victim] >= is_killer[k]
        problem += richer[k][victim] <= 1 - is_killer[k]

    # No one is richer than himself, and of two different people exactly one is richer.
    for i in people:
        problem += richer[i][i] == 0
        for j in people:
            if i < j:
                problem += richer[i][j] == 1 - richer[j][i]

    # Charles hates no one that Agatha hates.
    for i in people:
        problem += hates[charles][i] <= 1 - hates[agatha][i]

    # Agatha hates everybody except the butler.
    problem += hates[agatha][agatha] == 1
    problem += hates[agatha][charles] == 1
    problem += hates[agatha][butler] == 0

    # The butler hates everyone not richer than Aunt Agatha.
    for i in people:
        problem += hates[butler][i] >= 1 - richer[i][agatha]

    # The butler hates everyone whom Agatha hates.
    for i in people:
        problem += hates[butler][i] >= hates[agatha][i]

    # No one hates everyone.
    for i in people:
        problem += pulp.lpSum(hates[i]) <= n - 1

    return problem, {"killer": killer}
