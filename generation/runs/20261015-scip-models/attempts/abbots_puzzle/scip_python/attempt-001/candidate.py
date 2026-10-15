# Abbot's puzzle: 100 bushels of corn are given to 100 people (men, women, children)
# so that each man gets 3 bushels, each woman 2 and each child 1/2 bushel, with
# five times as many women as men. Find the number of men, women and children.
from pyscipopt import Model, quicksum


def build(instance):
    # The problem fixes these numbers: 100 bushels, 100 people, 3/2/0.5 bushels per
    # man/woman/child, and women = 5 * men. The instance has no fields.
    people = 100
    bushels = 100
    m = Model()
    men = m.addVar(name="men", vtype="I", lb=0, ub=people)
    women = m.addVar(name="women", vtype="I", lb=0, ub=people)
    children = m.addVar(name="children", vtype="I", lb=0, ub=people)

    # the 100 people are men, women and children
    m.addCons(men + women + children == people)

    # there are five times as many women as men
    m.addCons(women == 5 * men)

    # the 100 bushels are shared out: 3 per man, 2 per woman, 1/2 per child.
    # Multiplied by 2 to stay in integers: 6 per man, 4 per woman, 1 per child.
    m.addCons(6 * men + 4 * women + children == 2 * bushels)

    return m, {"men": men, "women": women, "children": children}
