# N-puzzle (sliding tiles): list the board at each of N_STEPS steps, from the
# start state to the end state, where every step slides one tile into the empty
# square (0) and the board changes at each step.
from ortools.sat.python import cp_model


def build(instance):
    n_steps = instance["N_STEPS"]  # boards in the solution, start and end included
    start = instance["puzzle_start"]  # 0 marks the empty square
    end = instance["puzzle_end"]
    dim = len(start)
    tiles = dim * dim - 1  # e.g. 8 tiles for a 3 x 3 board

    model = cp_model.CpModel()

    # steps[t][i][j] = the tile on square (i, j) at step t
    steps = [[[model.new_int_var(0, tiles, f"steps_{t}_{i}_{j}") for j in range(dim)] for i in range(dim)]
             for t in range(n_steps)]
    # empty[t][i][j] is true when square (i, j) is the empty one at step t
    empty = [[[model.new_bool_var(f"empty_{t}_{i}_{j}") for j in range(dim)] for i in range(dim)]
             for t in range(n_steps)]
    for t in range(n_steps):
        for i in range(dim):
            for j in range(dim):
                model.add(steps[t][i][j] == 0).only_enforce_if(empty[t][i][j])
                model.add(steps[t][i][j] != 0).only_enforce_if(empty[t][i][j].negated())

    # the first board is the start state and the last one the end state
    for i in range(dim):
        for j in range(dim):
            model.add(steps[0][i][j] == start[i][j])
            model.add(steps[n_steps - 1][i][j] == end[i][j])

    def near(i, j):
        """The square itself and its neighbours on the board (left, right, up, down)."""
        for di, dj in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
            if 0 <= i + di < dim and 0 <= j + dj < dim:
                yield i + di, j + dj

    for t in range(1, n_steps):
        prev, nxt = steps[t - 1], steps[t]
        # each board uses every tile once
        model.add_all_different([nxt[i][j] for i in range(dim) for j in range(dim)])
        changed = []
        for i in range(dim):
            for j in range(dim):
                # the empty square can only move to a neighbouring square: where it
                # is empty now it was empty here or on an adjacent square before
                model.add_bool_or([empty[t - 1][a][b] for a, b in near(i, j)]).only_enforce_if(empty[t][i][j])

                # only the empty square moves: a square that is neither empty
                # before nor empty after keeps its tile
                same = model.new_bool_var(f"same_{t}_{i}_{j}")
                model.add(prev[i][j] == nxt[i][j]).only_enforce_if(same)
                model.add(prev[i][j] != nxt[i][j]).only_enforce_if(same.negated())
                model.add_bool_or([empty[t - 1][i][j], empty[t][i][j], same])
                changed.append(same.negated())

        # the board must change at every step (no standing still)
        model.add_bool_or(changed)

    return model, {"steps": steps}
