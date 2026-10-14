"""Ages of the sons: three sons' ages multiply to 36 and add up to a number (the windows of a
building) that does not identify them, because another triple of ages with product 36 has the
same sum; the oldest son is a single person ("the oldest has blue eyes"). Find the ages.

The model reports the ages from the oldest. The puzzle has no instance data; its numbers are the
puzzle's own.
"""
from docplex.mp.model import Model


def build(instance):
    product = 36  # product of the ages (puzzle constant)
    top = 36      # the reference's bound on an age

    model = Model("ages_of_the_sons")

    # A product of three variables is not linear. It is stated as a table: the triples
    # x1 >= x2 >= x3 in 0..36 whose product is 36, of which exactly one is chosen.
    triples = [(x1, x2, x3) for x1 in range(top + 1) for x2 in range(x1 + 1) for x3 in range(x2 + 1)
               if x1 * x2 * x3 == product]

    # The sons' ages: the oldest is strictly older than the second, who is at least as old as
    # the third, and the ages multiply to 36.
    pick_a = {t: model.binary_var(name=f"a_{t[0]}_{t[1]}_{t[2]}") for t in triples if t[0] > t[1]}
    model.add_constraint(model.sum(pick_a.values()) == 1)

    # Another triple of ages, ordered from the oldest, with product 36.
    pick_b = {t: model.binary_var(name=f"b_{t[0]}_{t[1]}_{t[2]}") for t in triples}
    model.add_constraint(model.sum(pick_b.values()) == 1)

    def age(pick, k):
        return model.sum(t[k] * v for t, v in pick.items())

    # The other triple has a different oldest age ...
    model.add_constraint(age(pick_a, 0) != age(pick_b, 0))

    # ... and the same sum, so the number of windows does not settle the question.
    model.add_constraint(age(pick_a, 0) + age(pick_a, 1) + age(pick_a, 2)
                         == age(pick_b, 0) + age(pick_b, 1) + age(pick_b, 2))

    return model, {"A1": age(pick_a, 0), "A2": age(pick_a, 1), "A3": age(pick_a, 2)}
