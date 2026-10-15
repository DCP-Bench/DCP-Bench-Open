# Graph colouring: colour the countries so that neighbours get different colours, using as few colours as possible.
from pyscipopt import Model, quicksum


def build(instance):
    edges = instance["graph"]  # pairs of neighbouring countries, numbered from 1
    # the countries are numbered 1..n in the graph; n is the largest number used
    n = max(max(e) for e in edges)
    # a colouring never needs more colours than there are countries
    k_max = n

    m = Model("colouring")

    # x[i, c] = 1 if country i gets colour c (c = 0..k_max-1 stands for colour c+1)
    x = {(i, c): m.addVar(name=f"x_{i}_{c}", vtype="B") for i in range(n) for c in range(k_max)}
    # used[c] = 1 if colour c is used by some country
    used = {c: m.addVar(name=f"used_{c}", vtype="B") for c in range(k_max)}

    # each country gets exactly one colour
    for i in range(n):
        m.addCons(quicksum(x[i, c] for c in range(k_max)) == 1)

    # a colour is used only when some country has it
    for c in range(k_max):
        for i in range(n):
            m.addCons(x[i, c] <= used[c])

    # two neighbouring countries cannot have the same colour
    for a, b in edges:
        i, j = a - 1, b - 1
        for c in range(k_max):
            m.addCons(x[i, c] + x[j, c] <= 1)

    # symmetry breaking: colours are used in order, so colour c+1 is used only if colour c is
    for c in range(1, k_max):
        m.addCons(used[c] <= used[c - 1])

    # minimise the number of colours used
    m.setObjective(quicksum(used[c] for c in range(k_max)), "minimize")

    # the colour of each country as a number from 1
    colors = [quicksum((c + 1) * x[i, c] for c in range(k_max)) for i in range(n)]
    return m, {"colors": colors}
