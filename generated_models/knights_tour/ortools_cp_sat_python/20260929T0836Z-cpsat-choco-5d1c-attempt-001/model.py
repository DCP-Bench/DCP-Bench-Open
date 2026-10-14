# Knight's tour: number the squares of an n x n board 0..n*n-1 in the order a
# knight visits them, so that consecutive numbers are one knight's move apart
# and every square is visited exactly once (the tour does not have to return).
from ortools.sat.python import cp_model

KNIGHT_MOVES = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]


def build(instance):
    n = instance["n"]  # side of the board
    cells = n * n

    model = cp_model.CpModel()

    # x[i][j] = the move number at which the knight stands on square (i, j)
    x = [[model.new_int_var(0, cells - 1, f"x_{i}_{j}") for j in range(n)] for i in range(n)]
    model.add_all_different([x[i][j] for i in range(n) for j in range(n)])

    # The path is written as a circuit through the squares plus one extra node 0
    # that stands for "before the first move / after the last move"; this makes
    # the open tour a Hamiltonian circuit, which CP-SAT handles natively.
    # Squares are the circuit nodes 1..n*n, square (i, j) being node 1 + i*n + j.
    def node(i, j):
        return 1 + i * n + j

    arcs = []
    for i in range(n):
        for j in range(n):
            # the tour starts on this square (move number 0)
            first = model.new_bool_var(f"first_{i}_{j}")
            arcs.append((0, node(i, j), first))
            model.add(x[i][j] == 0).only_enforce_if(first)
            # the tour ends on this square (last move number)
            last = model.new_bool_var(f"last_{i}_{j}")
            arcs.append((node(i, j), 0, last))
            model.add(x[i][j] == cells - 1).only_enforce_if(last)
            # the knight jumps from this square to a square one knight's move away
            # and its move number goes up by one
            for di, dj in KNIGHT_MOVES:
                a, b = i + di, j + dj
                if 0 <= a < n and 0 <= b < n:
                    jump = model.new_bool_var(f"jump_{i}_{j}_{a}_{b}")
                    arcs.append((node(i, j), node(a, b), jump))
                    model.add(x[a][b] == x[i][j] + 1).only_enforce_if(jump)
    model.add_circuit(arcs)

    return model, {"x": x}
