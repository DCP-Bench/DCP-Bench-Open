"""Allergy logic puzzle: four friends (Debra, Janet, Hugh, Rick) each have a different surname
(Baxter, Lemon, Malone, Fleet) and a different allergy (eggs, mold, nuts, ragweed); match them
using the given clues.

The model reports, for each allergy and each surname, the friend it belongs to (Debra = 0,
Janet = 1, Hugh = 2, Rick = 3). The puzzle has no instance data; the clues are the puzzle's own.
"""
from docplex.mp.model import Model


def build(instance):
    n = 4  # four friends, four allergies, four surnames (puzzle constant)
    Debra, Janet, Hugh, Rick = range(n)
    friends = range(n)
    foods = ["eggs", "mold", "nuts", "ragweed"]
    surnames = ["baxter", "lemon", "malone", "fleet"]

    model = Model("allergy")

    # has[x, f] = 1 when allergy or surname x belongs to friend f. Within each group every item
    # belongs to one friend and every friend has one item (all different).
    has = {(x, f): model.binary_var(name=f"{x}_{f}") for x in foods + surnames for f in friends}
    for group in (foods, surnames):
        for x in group:
            model.add_constraint(model.sum(has[x, f] for f in friends) == 1)
        for f in friends:
            model.add_constraint(model.sum(has[x, f] for x in group) == 1)

    # Rick is not allergic to mold.
    model.add_constraint(has["mold", Rick] == 0)
    # Baxter is allergic to eggs.
    for f in friends:
        model.add_constraint(has["eggs", f] == has["baxter", f])
    # Hugh is neither surnamed Lemon nor Fleet.
    model.add_constraint(has["lemon", Hugh] == 0)
    model.add_constraint(has["fleet", Hugh] == 0)
    # Debra is allergic to ragweed.
    model.add_constraint(has["ragweed", Debra] == 1)
    # Janet (who isn't Lemon) is neither allergic to eggs nor to mold.
    model.add_constraint(has["lemon", Janet] == 0)
    model.add_constraint(has["eggs", Janet] == 0)
    model.add_constraint(has["mold", Janet] == 0)

    return model, {x: model.sum(f * has[x, f] for f in friends) for x in foods + surnames}
