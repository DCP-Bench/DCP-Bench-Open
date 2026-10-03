"""Abbot's puzzle: 100 bushels of corn are shared among 100 people, each man getting three bushels,
each woman two and each child half a bushel, with five times as many women as men. How many men,
women and children are there?

The model reports the numbers of men, women and children. The puzzle has no instance data; its
numbers are the puzzle's own and are written here as in the reference.
"""
from docplex.mp.model import Model


def build(instance):
    people = 100   # people sharing the corn (puzzle constant)
    bushels = 100  # bushels of corn shared (puzzle constant)

    model = Model("abbots_puzzle")

    men = model.integer_var(0, people, name="men")
    women = model.integer_var(0, people, name="women")
    children = model.integer_var(0, people, name="children")

    # There are 100 people in total.
    model.add_constraint(men + women + children == people)

    # They receive 100 bushels: 3 per man, 2 per woman, 1/2 per child (doubled to stay integral).
    model.add_constraint(6 * men + 4 * women + children == 2 * bushels)

    # There are five times as many women as men.
    model.add_constraint(5 * men == women)

    return model, {"men": men, "women": women, "children": children}
