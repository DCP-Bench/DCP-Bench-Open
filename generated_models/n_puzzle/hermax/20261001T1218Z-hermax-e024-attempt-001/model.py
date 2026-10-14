# N-puzzle: a sliding-tile puzzle on a square grid with one empty cell (0). Starting
# from the given board, move tiles into the empty cell, one move per step and never
# standing still, so that the board after N_STEPS - 1 moves is the given end board.
# The answer is the board at every step, start and end included.
import functools
import operator

from hermax.model import Model


def clause(*lits):
    """The disjunction of the given literals."""
    return functools.reduce(operator.or_, lits)


def exactly_one(m, lits, name):
    """Post "exactly one of lits is true" with a ladder encoding.

    prefix[i] says that one of lits[0..i] is true; each literal sets its prefix,
    prefixes carry on, and a literal after a set prefix is forbidden. That takes
    three clauses per literal, where forbidding every pair takes a quadratic number.
    """
    if len(lits) == 1:
        m &= lits[0]
        return
    prefix = m.bool_vector(name, len(lits))
    for i, lit in enumerate(lits):
        m &= (~lit | prefix[i])
        if i + 1 < len(lits):
            m &= (~prefix[i] | prefix[i + 1])
            m &= (~lits[i + 1] | ~prefix[i])
    m &= clause(*lits)


def build(instance):
    start = instance["puzzle_start"]  # start[i][j] = tile on the first board, 0 = empty cell
    end = instance["puzzle_end"]  # end[i][j] = tile on the last board
    n_steps = instance["N_STEPS"]  # number of boards, start and end included
    dim = len(start)
    n_cells = dim * dim
    n_tiles = n_cells - 1  # tiles are 1..n_tiles, 0 is the empty cell
    values = range(n_tiles + 1)

    m = Model()
    # holds[t][c][v] = at step t, cell c (numbered row by row) holds value v
    holds = [[[m.bool(f"holds_{t}_{c}_{v}") for v in values] for c in range(n_cells)]
             for t in range(n_steps)]
    # steps[t][i][j] = value of cell (i, j) at step t (the declared output)
    steps = [[[m.int(f"steps_{t}_{i}_{j}", 0, n_tiles) for j in range(dim)] for i in range(dim)]
             for t in range(n_steps)]

    # Every board is a full arrangement: each cell holds one value and each value
    # (every tile and the empty cell) sits in exactly one cell. This is the reference's
    # "all cells are different" invariant.
    for t in range(n_steps):
        for c in range(n_cells):
            exactly_one(m, [holds[t][c][v] for v in values], f"cell_{t}_{c}")
        for v in values:
            exactly_one(m, [holds[t][c][v] for c in range(n_cells)], f"value_{t}_{v}")

    # steps shows what is held: holding v means steps >= v and not steps >= v + 1
    # (comparisons that fall outside the range 0..n_tiles are already settled)
    for t in range(n_steps):
        for c in range(n_cells):
            i, j = divmod(c, dim)
            for v in values:
                if v > 0:
                    m &= (~holds[t][c][v] | (steps[t][i][j] >= v))
                if v < n_tiles:
                    m &= (~holds[t][c][v] | ~(steps[t][i][j] >= v + 1))

    # the first board is the start state and the last board is the end state
    for c in range(n_cells):
        i, j = divmod(c, dim)
        m &= holds[0][c][start[i][j]]
        m &= holds[n_steps - 1][c][end[i][j]]

    # The cells a move of the empty cell can reach: the cell itself or a side neighbour.
    def reach(c):
        i, j = divmod(c, dim)
        return [(i + di) * dim + (j + dj) for di, dj in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]
                if 0 <= i + di < dim and 0 <= j + dj < dim]

    for t in range(n_steps - 1):
        for c in range(n_cells):
            # the empty cell moves one cell sideways: if it is in cell c after the
            # move, it was in c or a neighbour of c before it
            m &= (~holds[t + 1][c][0] | clause(*[holds[t][d][0] for d in reach(c)]))
            # only the empty cell moves: a tile v in cell c stays there, unless the
            # empty cell moves into c (then c is empty afterwards)
            for v in range(1, n_tiles + 1):
                m &= (~holds[t][c][v] | holds[t + 1][c][v] | holds[t + 1][c][0])
            # The board must change at every step (no standing still). Given the rules
            # above a board changes exactly when the empty cell changes place, so the
            # empty cell may not be in the same cell before and after the move.
            m &= (~holds[t][c][0] | ~holds[t + 1][c][0])

    return m, {"steps": steps}
