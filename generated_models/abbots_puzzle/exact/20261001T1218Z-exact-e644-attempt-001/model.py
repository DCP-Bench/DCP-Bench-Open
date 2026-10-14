# Abbot's puzzle: 100 bushels of corn are shared among 100 people; each man gets 3 bushels, each
# woman 2 and each child half a bushel, and there are five times as many women as men. Find the
# number of men, women and children.
from exact import Exact


def build(instance):
    # This problem has no instance data. The numbers below belong to the problem statement itself:
    # 100 people, 100 bushels (200 half-bushels), five times as many women as men.
    people = 100
    half_bushels = 200  # bushels counted in halves so that every share is a whole number
    women_per_man = 5

    solver = Exact()

    # numbers of men, women and children, each between 0 and the number of people
    for name in ("men", "women", "children"):
        solver.addVariable(name, 0, people)

    # total number of people
    solver.addConstraint([(1, "men"), (1, "women"), (1, "children")], True, people, True, people)

    # total bushels of corn, in halves: a man gets 6 halves, a woman 4, a child 1
    solver.addConstraint([(6, "men"), (4, "women"), (1, "children")],
                         True, half_bushels, True, half_bushels)

    # five times as many women as men
    solver.addConstraint([(women_per_man, "men"), (-1, "women")], True, 0, True, 0)

    return solver, {"men": "men", "women": "women", "children": "children"}
