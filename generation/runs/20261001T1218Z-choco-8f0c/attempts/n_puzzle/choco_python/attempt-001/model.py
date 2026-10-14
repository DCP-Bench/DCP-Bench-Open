# N-puzzle: a sliding-tile puzzle on a square grid with one empty cell (0). Find the
# state of the grid at each of N_STEPS steps, from the start state to the end state,
# where every step slides one tile into the empty cell.
from pychoco.model import Model


def build(instance):
    n_steps = instance["N_STEPS"]  # number of states, including the start and end states
    puzzle_start = instance["puzzle_start"]
    puzzle_end = instance["puzzle_end"]
    dim = len(puzzle_start)  # the grid is dim x dim
    n = dim * dim - 1  # tiles are numbered 1..n, 0 is the empty cell

    model = Model()

    # steps[t][i][j] = tile in row i, column j at step t (0 = empty cell)
    steps = [[[model.intvar(0, n, name=f"steps_{t}_{i}_{j}") for j in range(dim)]
              for i in range(dim)] for t in range(n_steps)]
    # empty[t][i][j] is true when the cell (i, j) is the empty cell at step t
    empty = [[[model.arithm(steps[t][i][j], "=", 0).reify() for j in range(dim)]
              for i in range(dim)] for t in range(n_steps)]

    # the first state is the start state and the last state is the end state
    for i in range(dim):
        for j in range(dim):
            model.arithm(steps[0][i][j], "=", puzzle_start[i][j]).post()
            model.arithm(steps[-1][i][j], "=", puzzle_end[i][j]).post()

    def neighbours(i, j):
        # the cell itself and its left, right, up and down neighbours, if within the grid
        for di, dj in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
            if 0 <= i + di < dim and 0 <= j + dj < dim:
                yield i + di, j + dj

    for t in range(1, n_steps):
        prev, nxt = steps[t - 1], steps[t]

        # the empty cell can only move to a neighbouring cell: if a cell is empty in the
        # next state, then the empty cell was in that cell or next to it in the previous state
        for i in range(dim):
            for j in range(dim):
                came_from = [empty[t - 1][r][c] for r, c in neighbours(i, j)]
                model.sum(came_from, ">=", empty[t][i][j]).post()

        # all tiles of a state are different
        model.all_different([nxt[i][j] for i in range(dim) for j in range(dim)]).post()

        # only the empty cell moves: a cell that is not empty in either state keeps its tile
        unchanged = []
        for i in range(dim):
            for j in range(dim):
                same = model.arithm(prev[i][j], "=", nxt[i][j]).reify()
                unchanged.append(same)
                model.sum([empty[t - 1][i][j], empty[t][i][j], same], ">=", 1).post()

        # the state must change at every step (no freezing): not every cell is unchanged
        model.sum(unchanged, "<", dim * dim).post()

    return model, {"steps": steps}
