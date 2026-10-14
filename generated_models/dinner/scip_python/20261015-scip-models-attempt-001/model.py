# Dinner: choose numbers of grandparents, parents and children so that 20 people
# eat dinner and the bill is exactly $20 (grandparents $3, parents $2, children $0.50).
from pyscipopt import Model, quicksum


def build(instance):
    m = Model()
    # the problem's own domains: 1-6 grandparents, 1-10 parents, 1-40 children
    grandparents = m.addVar(name="grandparents", vtype="I", lb=1, ub=6)
    parents = m.addVar(name="parents", vtype="I", lb=1, ub=10)
    children = m.addVar(name="children", vtype="I", lb=1, ub=40)

    # there must be 20 total people at dinner
    m.addCons(grandparents + parents + children == 20)
    # it must cost $20; multiplied by 2 so every coefficient is an integer
    # (grandparents $3 -> 6, parents $2 -> 4, children $0.50 -> 1, total $20 -> 40)
    m.addCons(6 * grandparents + 4 * parents + children == 40)

    outputs = {
        "grandparents": grandparents,
        "parents": parents,
        "children": children,
    }
    return m, outputs
