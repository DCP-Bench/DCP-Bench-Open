# Calvin puzzle: number the squares of an n x n grid 1..n*n in sequence so
# that each next number lies exactly three squares away horizontally or
# vertically (two squares between them), or exactly two squares away along a
# diagonal (one square between them).
from ortools.sat.python import cp_model

# the allowed jumps (row change, column change)
MOVES = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]


def build(instance):
    n = instance["n"]  # side of the grid
    cells = n * n

    model = cp_model.CpModel()

    # x[i][j] = the number written in square (i, j); every number is used once
    x = [[model.new_int_var(1, cells, f"x_{i}_{j}") for j in range(n)] for i in range(n)]
    model.add_all_different([x[i][j] for i in range(n) for j in range(n)])

    # The sequence of squares is an open path through the whole grid, written as
    # a circuit through the squares plus one extra node 0 standing for "before
    # the first number / after the last number". Square (i, j) is node 1 + i*n + j.
    def node(i, j):
        return 1 + i * n + j

    arcs = []
    for i in range(n):
        for j in range(n):
            # the path starts here, with number 1
            first = model.new_bool_var(f"first_{i}_{j}")
            arcs.append((0, node(i, j), first))
            model.add(x[i][j] == 1).only_enforce_if(first)
            # the path ends here, with the largest number
            last = model.new_bool_var(f"last_{i}_{j}")
            arcs.append((node(i, j), 0, last))
            model.add(x[i][j] == cells).only_enforce_if(last)
            # the next number goes one allowed jump away and is one larger
            for di, dj in MOVES:
                a, b = i + di, j + dj
                if 0 <= a < n and 0 <= b < n:
                    jump = model.new_bool_var(f"jump_{i}_{j}_{a}_{b}")
                    arcs.append((node(i, j), node(a, b), jump))
                    model.add(x[a][b] == x[i][j] + 1).only_enforce_if(jump)
    model.add_circuit(arcs)

    return model, {"x": x}
