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
    cells = dim * dim  # cell (i, j) has number i * dim + j

    model = Model()

    # steps[t][i][j] = tile in row i, column j at step t (0 = empty cell)
    steps = [[[model.intvar(0, n, name=f"steps_{t}_{i}_{j}") for j in range(dim)]
              for i in range(dim)] for t in range(n_steps)]
    flat = [[steps[t][i][j] for i in range(dim) for j in range(dim)] for t in range(n_steps)]
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
        model.all_different(flat[t]).post()

        # only the empty cell moves: a cell that is not empty in either state keeps its tile
        unchanged = []
        for i in range(dim):
            for j in range(dim):
                same = model.arithm(prev[i][j], "=", nxt[i][j]).reify()
                unchanged.append(same)
                model.sum([empty[t - 1][i][j], empty[t][i][j], same], ">=", 1).post()

        # the state must change at every step (no freezing): not every cell is unchanged
        model.sum(unchanged, "<", dim * dim).post()

    # ---- Implied constraints. They follow from the constraints above, so they do not
    # change which sequences of states are allowed; they only give the solver earlier
    # failures, which matters for puzzles with a long solution.

    # position[t][k] = cell number holding tile k at step t (k = 0: the empty cell)
    position = [[model.intvar(0, cells - 1, name=f"position_{t}_{k}") for k in range(cells)]
                for t in range(n_steps)]
    for t in range(n_steps):
        model.inverse_channeling(flat[t], position[t]).post()

    # the empty cell moves to an adjacent cell at every step
    adjacent_cells = [[a, b] for a in range(cells) for b in range(cells)
                      if abs(a // dim - b // dim) + abs(a % dim - b % dim) == 1]
    for t in range(1, n_steps):
        model.table([position[t - 1][0], position[t][0]], adjacent_cells).post()

    # the tile that was on the cell the empty cell moves to slides into the cell the
    # empty cell leaves
    for t in range(1, n_steps):
        moved = model.intvar(1, n, name=f"moved_{t}")
        model.element(moved, flat[t - 1], position[t][0]).post()
        model.element(moved, flat[t], position[t - 1][0]).post()

    # each step moves one tile by one cell, so it lowers the sum over tiles of the
    # (Manhattan) distance of the tile to its place in the end state by at most 1:
    # at step t that sum cannot exceed the number of steps still to come.
    goal_cell = {puzzle_end[i][j]: i * dim + j for i in range(dim) for j in range(dim)}
    for t in range(n_steps):
        distances = []
        for k in range(1, cells):
            gr, gc = divmod(goal_cell[k], dim)
            distance_to_goal = [abs(c // dim - gr) + abs(c % dim - gc) for c in range(cells)]
            distance = model.intvar(0, 2 * (dim - 1), name=f"distance_{t}_{k}")
            model.element(distance, distance_to_goal, position[t][k]).post()
            distances.append(distance)
        model.sum(distances, "<=", n_steps - 1 - t).post()

    return model, {"steps": steps}
