# N-puzzle (sliding tiles): go from the start board to the end board in exactly N_STEPS boards
# (start and end included). At every step the empty tile (0) swaps places with a tile next to it,
# so the board changes at every step.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n_steps = instance["N_STEPS"]  # number of boards in the plan, including the start and the end
    start = instance["puzzle_start"]
    end = instance["puzzle_end"]
    dim = len(start)               # the board is dim x dim
    tiles = dim * dim - 1          # tiles 1..tiles, and 0 for the empty place

    pool = IDPool()
    # board[t][i][j] = the tile in row i, column j at step t
    board = [[[Integer(f"b_{t}_{i}_{j}", 0, tiles, vpool=pool) for j in range(dim)] for i in range(dim)]
             for t in range(n_steps)]
    engine = IntegerEngine(vars=[cell for step in board for row in step for cell in row], vpool=pool)

    # at every step all tiles (and the empty place) are in different cells
    for step in board:
        engine.add_alldifferent([cell for row in step for cell in row])
    cnf = engine.clausify()

    # the first board is the start state and the last board is the end state
    for i in range(dim):
        for j in range(dim):
            cnf.append([board[0][i][j].equals(start[i][j])])
            cnf.append([board[-1][i][j].equals(end[i][j])])

    def around(i, j):
        """The cell itself and its neighbours to the left, right, above and below, inside the board."""
        return [(i + di, j + dj) for di, dj in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]
                if 0 <= i + di < dim and 0 <= j + dj < dim]

    for t in range(1, n_steps):
        before, after = board[t - 1], board[t]
        differs = []
        for i in range(dim):
            for j in range(dim):
                # the empty place of the next board is where the empty place was or next to it
                cnf.append([-after[i][j].equals(0)] + [before[r][c].equals(0) for r, c in around(i, j)])

                # only the empty place moves: a tile that is in a cell and not in the empty place
                # in the next board stays; so if the cell holds tile v before, it holds v or the
                # empty place after
                for v in range(1, tiles + 1):
                    cnf.append([-before[i][j].equals(v), after[i][j].equals(v), after[i][j].equals(0)])

                # differs is true only if this cell holds different values before and after
                flag = pool.id(("differs", t, i, j))
                for v in range(tiles + 1):
                    cnf.append([-flag, -before[i][j].equals(v), -after[i][j].equals(v)])
                differs.append(flag)

        # the board changes at every step (no freezing)
        cnf.append(differs)

    return cnf, {"steps": board}
