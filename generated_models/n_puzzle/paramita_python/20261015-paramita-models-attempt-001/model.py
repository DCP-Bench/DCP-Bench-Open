# N-Puzzle: a sliding-tile puzzle on an n x n grid. Trace the steps from the
# start picture to the end picture; each step moves one tile into the empty
# tile (value 0), and the state must change at every step.
# Each state s, cell (r, c) and tile value v has a Bool p[s][r][c][v], meaning
# "cell (r, c) holds tile v in state s" (one-hot encoding).
from paramita.modelling import Bool, If


def build(instance):
    start = instance["puzzle_start"]
    end = instance["puzzle_end"]
    steps = instance["N_STEPS"]
    n = len(start)
    n_values = n * n          # tiles 0 (empty) .. n*n-1
    cells = [(r, c) for r in range(n) for c in range(n)]

    def adjacent(q, q2):
        return abs(q[0] - q2[0]) + abs(q[1] - q2[1]) == 1

    p = [[[[Bool(f"p_{s}_{r}_{c}_{v}") for v in range(n_values)]
           for c in range(n)]
          for r in range(n)]
         for s in range(steps)]

    def at(s, q, v):
        return p[s][q[0]][q[1]][v]

    cons = []

    # every cell of every state holds exactly one tile
    for s in range(steps):
        for q in cells:
            cons.append(sum(at(s, q, v) for v in range(n_values)) == 1)

    # every state holds each tile exactly once (the tiles form a permutation)
    for s in range(steps):
        for v in range(n_values):
            cons.append(sum(at(s, q, v) for q in cells) == 1)

    # the start picture is given by the instance
    for r in range(n):
        for c in range(n):
            cons.append(at(0, (r, c), start[r][c]))

    # the end picture is given by the instance
    for r in range(n):
        for c in range(n):
            cons.append(at(steps - 1, (r, c), end[r][c]))

    # a move slides one tile into the empty tile: a tile can only move to a
    # neighbouring cell, and the empty tile moves into the cell it left
    for s in range(steps - 1):
        for q in cells:
            for q2 in cells:
                if q == q2:
                    continue
                if not adjacent(q, q2):
                    for v in range(n_values):
                        cons.append(~(at(s, q, v) & at(s + 1, q2, v)))
                    continue
                for v in range(1, n_values):
                    cons.append(If(at(s, q, v) & at(s + 1, q2, v),
                                   at(s, q2, 0) & at(s + 1, q, 0)))

    # freezing is not allowed: the empty tile's cell changes at each step
    for s in range(steps - 1):
        for q in cells:
            cons.append(~(at(s, q, 0) & at(s + 1, q, 0)))

    # print the state of the puzzle at each step as a grid of integers
    state = [[[sum(v * at(s, (r, c), v) for v in range(n_values))
               for c in range(n)]
              for r in range(n)]
             for s in range(steps)]

    return cons, {"steps": state}
