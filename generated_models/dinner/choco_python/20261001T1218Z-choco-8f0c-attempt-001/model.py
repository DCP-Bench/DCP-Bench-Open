# Dinner: take 1-6 grandparents ($3 each), 1-10 parents ($2) and 1-40 children ($0.50) to dinner,
# 20 people in all for $20. How many of each go?
from pychoco.model import Model

# The puzzle has no instance data; the ranges, prices and totals are its statement.


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    # "taking 1-6 grandparents, 1-10 parents and/or 1-40 children"
    grandparents = model.intvar(1, 6, name="grandparents")
    parents = model.intvar(1, 10, name="parents")
    children = model.intvar(1, 40, name="children")

    # Dinner costs $20: $3, $2 and $0.50 a head, doubled so the half dollar is whole.
    model.scalar([grandparents, parents, children], [6, 4, 1], "=", 20 * 2).post()
    # There are 20 people at dinner.
    model.sum([grandparents, parents, children], "=", 20).post()

    return model, {"grandparents": grandparents, "parents": parents, "children": children}
