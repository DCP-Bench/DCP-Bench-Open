# Quasigroup completion: fill the empty cells of an order-m Latin square so that
# every row and every column contains each symbol 1..m exactly once.
from pyscipopt import Model, quicksum


def build(instance):
    m_order = instance["N"]
    start = instance["start"]
    R = range(m_order)
    V = range(1, m_order + 1)

    model = Model("quasigroup_completion")

    # x[i, j, v] = 1 if the cell in row i, column j holds symbol v
    x = {(i, j, v): model.addVar(name=f"x_{i}_{j}_{v}", vtype="B")
         for i in R for j in R for v in V}

    # each cell of the square holds exactly one symbol
    for i in R:
        for j in R:
            model.addCons(quicksum(x[i, j, v] for v in V) == 1)

    # each symbol occurs exactly once in every row
    for i in R:
        for v in V:
            model.addCons(quicksum(x[i, j, v] for j in R) == 1)

    # each symbol occurs exactly once in every column
    for j in R:
        for v in V:
            model.addCons(quicksum(x[i, j, v] for i in R) == 1)

    # the given cells keep their pre-filled symbols (0 marks an empty cell)
    for i in R:
        for j in R:
            given = start[i][j]
            if given != 0:
                model.addCons(x[i, j, given] == 1)

    # the output is the completed table, value of each cell
    puzzle = [[quicksum(v * x[i, j, v] for v in V) for j in R] for i in R]
    return model, {"puzzle": puzzle}
