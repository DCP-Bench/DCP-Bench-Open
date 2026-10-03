"""Who killed Agatha: Agatha, the butler and Charles live in Dreadsbury Mansion and one of
them killed Agatha. From who hates whom and who is richer, find the killer.
"""
from docplex.mp.model import Model


def build(instance):
    names = instance["names"]  # the residents; the statement lists Agatha, the butler, Charles
    n = len(names)
    people = range(n)
    agatha, butler, charles = 0, 1, 2
    victim = agatha

    model = Model("who_killed_agatha")

    hates = {(i, j): model.binary_var(name=f"hates_{i}_{j}") for i in people for j in people}
    richer = {(i, j): model.binary_var(name=f"richer_{i}_{j}") for i in people for j in people}

    # is_killer[i] is 1 when resident i is the killer; exactly one of them.
    is_killer = [model.binary_var(name=f"killer_is_{i}") for i in people]
    model.add_constraint(model.sum(is_killer) == 1)

    # A killer always hates, and is no richer than, his victim.
    for i in people:
        model.add_constraint(is_killer[i] <= hates[i, victim])
        model.add_constraint(is_killer[i] <= 1 - richer[i, victim])

    # No one is richer than himself, and of two different people exactly one is richer.
    for i in people:
        model.add_constraint(richer[i, i] == 0)
        for j in people:
            if i < j:
                model.add_constraint(richer[i, j] == 1 - richer[j, i])

    # Charles hates no one that Agatha hates.
    for i in people:
        model.add_constraint(hates[agatha, i] + hates[charles, i] <= 1)

    # Agatha hates everybody except the butler.
    model.add_constraint(hates[agatha, agatha] == 1)
    model.add_constraint(hates[agatha, charles] == 1)
    model.add_constraint(hates[agatha, butler] == 0)

    # The butler hates everyone not richer than Aunt Agatha.
    for i in people:
        model.add_constraint(1 - richer[i, agatha] <= hates[butler, i])

    # The butler hates everyone whom Agatha hates.
    for i in people:
        model.add_constraint(hates[agatha, i] <= hates[butler, i])

    # No one hates everyone.
    for i in people:
        model.add_constraint(model.sum(hates[i, j] for j in people) <= n - 1)

    # The killer's 0-based index.
    killer = model.integer_var(0, n - 1, name="killer")
    model.add_constraint(killer == model.sum(i * is_killer[i] for i in people))

    return model, {"killer": killer}
