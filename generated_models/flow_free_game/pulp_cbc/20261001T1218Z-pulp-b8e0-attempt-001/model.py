"""Flow Free: connect the matching coloured endpoints on the board with pipes that cover every
cell and never cross. Each endpoint has exactly one neighbour of its colour, and every other
cell has exactly two, so the cells of a colour form a path between its endpoints.

The model reports the coloured board B.
"""
import pulp


def build(instance):
    board = instance["board"]
    rows, cols = len(board), len(board[0])
    cells = [(i, j) for i in range(rows) for j in range(cols)]
    colors = range(1, 11)  # a cell's colour lies in 1..10, the reference's domain

    problem = pulp.LpProblem("flow_free_game", pulp.LpMinimize)  # satisfaction

    # colored[cell][c] = 1 if the cell has colour c; every cell has one colour
    colored = {cell: {c: pulp.LpVariable(f"colored_{cell[0]}_{cell[1]}_{c}", cat="Binary")
                      for c in colors} for cell in cells}
    for cell in cells:
        problem += pulp.lpSum(colored[cell].values()) == 1

    # the given endpoints keep their colour
    for (i, j) in cells:
        if board[i][j] != 0:
            problem += colored[(i, j)][board[i][j]] == 1

    # same[u, v] = 1 if neighbouring cells u and v have the same colour: both[c] is the
    # product of the two colour indicators, and at most one colour can have it
    same = {}
    for (i, j) in cells:
        for (k, l) in ((i + 1, j), (i, j + 1)):
            if k < rows and l < cols:
                u, v = (i, j), (k, l)
                terms = []
                for c in colors:
                    both = pulp.LpVariable(f"both_{i}_{j}_{k}_{l}_{c}", cat="Binary")
                    problem += both <= colored[u][c]
                    problem += both <= colored[v][c]
                    problem += both >= colored[u][c] + colored[v][c] - 1
                    terms.append(both)
                same[u, v] = same[v, u] = pulp.lpSum(terms)

    # an endpoint has exactly one neighbour of its colour; any other cell has exactly two
    for (i, j) in cells:
        neighbours = [(k, l) for (k, l) in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1))
                      if 0 <= k < rows and 0 <= l < cols]
        alike = pulp.lpSum(same[(i, j), nb] for nb in neighbours)
        problem += alike == (1 if board[i][j] != 0 else 2)

    B = [[pulp.lpSum(c * colored[(i, j)][c] for c in colors) for j in range(cols)]
         for i in range(rows)]
    return problem, {"B": B}
