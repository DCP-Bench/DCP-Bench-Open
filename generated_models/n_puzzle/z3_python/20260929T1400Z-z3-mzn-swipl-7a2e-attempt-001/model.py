# N-puzzle (sliding tiles): list the board at each of N_STEPS steps, from the
# start state to the end state, where every step slides one tile into the empty
# square (0) and the board changes at each step.
import z3


def build(instance):
    n_steps = instance["N_STEPS"]  # boards in the solution, start and end included
    start = instance["puzzle_start"]  # 0 marks the empty square
    end = instance["puzzle_end"]
    dim = len(start)
    tiles = dim * dim - 1  # e.g. 8 tiles for a 3 x 3 board

    solver = z3.Solver()

    # steps[t][i][j] = the tile on square (i, j) at step t
    steps = [[[z3.Int(f"steps_{t}_{i}_{j}") for j in range(dim)] for i in range(dim)] for t in range(n_steps)]
    for t in range(n_steps):
        for i in range(dim):
            for j in range(dim):
                solver.add(steps[t][i][j] >= 0, steps[t][i][j] <= tiles)

    # the first board is the start state and the last one the end state
    for i in range(dim):
        for j in range(dim):
            solver.add(steps[0][i][j] == start[i][j])
            solver.add(steps[n_steps - 1][i][j] == end[i][j])

    def near(i, j):
        """The square itself and its neighbours on the board (left, right, up, down)."""
        for di, dj in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
            if 0 <= i + di < dim and 0 <= j + dj < dim:
                yield i + di, j + dj

    for t in range(1, n_steps):
        prev, nxt = steps[t - 1], steps[t]
        # each board uses every tile once
        solver.add(z3.Distinct([nxt[i][j] for i in range(dim) for j in range(dim)]))
        for i in range(dim):
            for j in range(dim):
                # the empty square can only move to a neighbouring square: where it
                # is empty now it was empty here or on an adjacent square before
                solver.add(z3.Implies(nxt[i][j] == 0, z3.Or([prev[a][b] == 0 for a, b in near(i, j)])))
                # only the empty square moves: a square that is neither empty
                # before nor empty after keeps its tile
                solver.add(z3.Or(prev[i][j] == 0, nxt[i][j] == 0, prev[i][j] == nxt[i][j]))
        # the board must change at every step (no standing still)
        solver.add(z3.Or([prev[i][j] != nxt[i][j] for i in range(dim) for j in range(dim)]))

    return solver, {"steps": steps}
