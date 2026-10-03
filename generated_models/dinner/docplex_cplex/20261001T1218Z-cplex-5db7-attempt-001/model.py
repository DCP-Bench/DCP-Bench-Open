"""Dinner: 20 people go to dinner for $20 in total; grandparents cost $3, parents $2 and
children $0.50. How many of each go?
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data; every number below is from the statement.
    model = Model("dinner")

    # 1-6 grandparents, 1-10 parents and 1-40 children.
    grandparents = model.integer_var(1, 6, name="grandparents")
    parents = model.integer_var(1, 10, name="parents")
    children = model.integer_var(1, 40, name="children")

    # The dinner costs $20: $3 a grandparent, $2 a parent, $0.50 a child, counted in half
    # dollars so every coefficient is an integer.
    model.add_constraint(6 * grandparents + 4 * parents + children == 2 * 20)
    # There are 20 people in total.
    model.add_constraint(grandparents + parents + children == 20)

    return model, {"grandparents": grandparents, "parents": parents, "children": children}
