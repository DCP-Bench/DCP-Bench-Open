"""Five floors (Dinesman): Baker, Cooper, Fletcher, Miller and Smith live on different floors
of a five-floor house; find each one's floor from the clues.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data: five people, floors 1..5.
    people = ["B", "C", "F", "M", "S"]  # Baker, Cooper, Fletcher, Miller, Smith
    floors = range(1, 6)

    model = Model("five_floors")

    # lives[p, f] is 1 when person p lives on floor f; one floor each, and they all live on
    # different floors.
    lives = {(p, f): model.binary_var(name=f"{p}_on_{f}") for p in people for f in floors}
    for p in people:
        model.add_constraint(model.sum(lives[p, f] for f in floors) == 1)
    for f in floors:
        model.add_constraint(model.sum(lives[p, f] for p in people) == 1)
    floor = {p: model.integer_var(1, 5, name=p) for p in people}
    for p in people:
        model.add_constraint(floor[p] == model.sum(f * lives[p, f] for f in floors))

    # Baker does not live on the fifth floor.
    model.add_constraint(lives["B", 5] == 0)
    # Cooper does not live on the first floor.
    model.add_constraint(lives["C", 1] == 0)
    # Fletcher lives on neither the fifth nor the first floor.
    model.add_constraint(lives["F", 5] + lives["F", 1] == 0)
    # Miller lives on a higher floor than Cooper.
    model.add_constraint(floor["M"] >= floor["C"] + 1)

    def not_adjacent(p, q):
        # p and q do not live on neighbouring floors f and f + 1, in either order.
        for f in floors:
            if f + 1 in floors:
                model.add_constraint(lives[p, f] + lives[q, f + 1] <= 1)
                model.add_constraint(lives[p, f + 1] + lives[q, f] <= 1)

    # Smith does not live on a floor adjacent to Fletcher's.
    not_adjacent("S", "F")
    # Fletcher does not live on a floor adjacent to Cooper's.
    not_adjacent("F", "C")

    return model, dict(floor)
