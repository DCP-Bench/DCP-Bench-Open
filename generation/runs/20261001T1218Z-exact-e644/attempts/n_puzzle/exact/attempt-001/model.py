# N-puzzle: a square grid holds the tiles 1..n and one empty cell (0). A move slides a tile into the
# empty cell. Give the state of the board at each of N_STEPS consecutive steps, from the start
# state to the end state, where every step is a move (the board must change).
from exact import Exact


def build(instance):
    n_steps = instance["N_STEPS"]  # number of states, including the start and the end state
    start = instance["puzzle_start"]
    end = instance["puzzle_end"]
    dim = len(start)
    cells = [(i, j) for i in range(dim) for j in range(dim)]
    tiles = range(dim * dim)  # 0 is the empty cell, 1..dim*dim-1 the tiles

    solver = Exact()

    # holds[t][i][j][v] = 1 when, at step t, cell (i, j) holds v. Exact has no all-different or
    # element constraint, so the board state is a 0/1 grid of indicators.
    holds = [[[[f"step_{t}_cell_{i}_{j}_holds_{v}" for v in tiles] for j in range(dim)]
              for i in range(dim)] for t in range(n_steps)]
    # steps[t][i][j] is the value in cell (i, j) at step t
    steps = [[[f"steps_{t}_{i}_{j}" for j in range(dim)] for i in range(dim)] for t in range(n_steps)]
    for t in range(n_steps):
        for i, j in cells:
            solver.addVariable(steps[t][i][j], 0, dim * dim - 1)
            for name in holds[t][i][j]:
                solver.addVariable(name, 0, 1)
            # every cell holds exactly one value, and steps is that value
            solver.addConstraint([(1, name) for name in holds[t][i][j]], True, 1, True, 1)
            solver.addConstraint([(v, holds[t][i][j][v]) for v in tiles if v] + [(-1, steps[t][i][j])],
                                 True, 0, True, 0)
        # in each state all cells are different: every value is in exactly one cell
        for v in tiles:
            solver.addConstraint([(1, holds[t][i][j][v]) for i, j in cells], True, 1, True, 1)

    # the first state is the start state and the last one is the end state
    for i, j in cells:
        solver.addConstraint([(1, holds[0][i][j][start[i][j]])], True, 1, True, 1)
        solver.addConstraint([(1, holds[n_steps - 1][i][j][end[i][j]])], True, 1, True, 1)

    def neighbours(i, j):
        """The cells next to (i, j) (left, right, up, down), inside the board."""
        return [(i + a, j + b) for a, b in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                if 0 <= i + a < dim and 0 <= j + b < dim]

    # a move between consecutive states
    for t in range(n_steps - 1):
        for i, j in cells:
            # the empty cell moves to an adjacent cell: it is at (i, j) in the next state only if
            # it was next to (i, j) before. The board must change at every step, so the empty cell
            # cannot stay where it is (staying would leave every cell as it was).
            solver.addConstraint([(1, holds[t][ni][nj][0]) for ni, nj in neighbours(i, j)]
                                 + [(-1, holds[t + 1][i][j][0])], True, 0)
            # only the empty cell moves: a cell that is not empty before or after keeps its value
            for v in tiles:
                if v:
                    solver.addConstraint([(1, holds[t][i][j][v]), (-1, holds[t + 1][i][j][v]),
                                          (1, holds[t][i][j][0]), (1, holds[t + 1][i][j][0])], True, 0)
                    solver.addConstraint([(-1, holds[t][i][j][v]), (1, holds[t + 1][i][j][v]),
                                          (1, holds[t][i][j][0]), (1, holds[t + 1][i][j][0])], True, 0)

    return solver, {"steps": steps}
