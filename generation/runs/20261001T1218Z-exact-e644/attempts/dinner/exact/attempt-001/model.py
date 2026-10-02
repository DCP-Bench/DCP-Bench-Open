# Dinner: a party of grandparents, parents and children goes out; there are 20 people in total and
# the bill is exactly $20. Find how many of each go.
from exact import Exact


def build(instance):
    # This problem has no instance data. The head-count ranges, the prices and the totals belong to
    # the problem statement.
    people, budget = 20, 20

    solver = Exact()
    # "taking 1-6 grandparents, 1-10 parents and/or 1-40 children"
    solver.addVariable("grandparents", 1, 6)
    solver.addVariable("parents", 1, 10)
    solver.addVariable("children", 1, 40)

    # There must be 20 people at dinner.
    solver.addConstraint([(1, "grandparents"), (1, "parents"), (1, "children")],
                         True, people, True, people)
    # The bill is $20. Grandparents cost $3, parents $2 and children $0.50; every price is doubled
    # (6, 4, 1) so that all coefficients are integers, which makes the right-hand side 2 * 20.
    solver.addConstraint([(6, "grandparents"), (4, "parents"), (1, "children")],
                         True, 2 * budget, True, 2 * budget)

    return solver, {"grandparents": "grandparents", "parents": "parents", "children": "children"}
