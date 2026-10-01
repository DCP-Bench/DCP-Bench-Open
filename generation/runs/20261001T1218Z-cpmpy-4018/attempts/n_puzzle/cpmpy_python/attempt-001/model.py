# N-puzzle (sliding tiles): a square grid has tiles 1..n and one empty square (0). Find the
# sequence of N_STEPS board states from the start state to the end state, where each state
# follows from the previous one by sliding one tile into the empty square.
import cpmpy as cp


def build(instance):
    n_steps = instance["N_STEPS"]       # number of states, counting the start and end states
    start = instance["puzzle_start"]
    end = instance["puzzle_end"]
    dim = len(start)
    n_tiles = dim * dim - 1             # e.g. 8 tiles for the 3 x 3 puzzle

    # steps[t, i, j] = tile in row i, column j at step t (0 = empty square)
    steps = cp.intvar(0, n_tiles, shape=(n_steps, dim, dim), name="steps")

    model = cp.Model()

    # The first state is the start state and the last state is the end state.
    for i in range(dim):
        for j in range(dim):
            model += steps[0, i, j] == start[i][j]
            model += steps[n_steps - 1, i, j] == end[i][j]

    def around(i, j):
        # the square itself and its neighbours to the left, right, above and below, inside the grid
        return [(i + a, j + b) for a, b in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]
                if 0 <= i + a < dim and 0 <= j + b < dim]

    for t in range(1, n_steps):
        prev, nxt = steps[t - 1], steps[t]

        # The empty square can only end up where it was or on a neighbouring square.
        for i in range(dim):
            for j in range(dim):
                model += (nxt[i, j] == 0).implies(cp.any([prev[r, c] == 0 for r, c in around(i, j)]))

        # Every state holds each tile exactly once.
        model += cp.AllDifferent(nxt)

        # Only the empty square moves: at each position the tile is the same in both states,
        # or the empty square is there before or after.
        for i in range(dim):
            for j in range(dim):
                model += (prev[i, j] == 0) | (nxt[i, j] == 0) | (prev[i, j] == nxt[i, j])

        # The board must change at every step (no standing still).
        model += cp.any([prev[i, j] != nxt[i, j] for i in range(dim) for j in range(dim)])

    return model, {"steps": steps}
