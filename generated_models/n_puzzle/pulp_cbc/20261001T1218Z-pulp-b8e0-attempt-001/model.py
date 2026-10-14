"""N-puzzle: a square board holds the numbered tiles 1..n and one empty square (0). A move
slides a tile next to the empty square into it. Starting from the given board, reach the
given end board in exactly N_STEPS boards (the start and the end included), where the board
must change at every step.

The model reports the board at every step.
"""
import pulp


def build(instance):
    n_steps = instance["N_STEPS"]  # number of boards, the start and the end included
    start = instance["puzzle_start"]  # start board, 0 is the empty square
    end = instance["puzzle_end"]  # end board
    dim = len(start)  # the board is dim x dim
    cells = [(i, j) for i in range(dim) for j in range(dim)]
    values = range(dim * dim)  # 0 (empty square) and the tiles 1..dim*dim-1

    problem = pulp.LpProblem("n_puzzle", pulp.LpMinimize)  # satisfaction: no objective

    # board[t][(i, j)][v] = 1 if square (i, j) holds the value v at step t. At every step each
    # square holds one value and each value is on one square (the values are all different
    # and there are as many values as squares).
    board = [{(cell, v): pulp.LpVariable(f"board_{t}_{cell[0]}_{cell[1]}_{v}", cat="Binary")
              for cell in cells for v in values} for t in range(n_steps)]
    for t in range(n_steps):
        for cell in cells:
            problem += pulp.lpSum(board[t][(cell, v)] for v in values) == 1
        for v in values:
            problem += pulp.lpSum(board[t][(cell, v)] for cell in cells) == 1

    # the board at step 0 is the start board and the board at the last step is the end board
    for cell in cells:
        problem += board[0][(cell, start[cell[0]][cell[1]])] == 1
        problem += board[n_steps - 1][(cell, end[cell[0]][cell[1]])] == 1

    # the squares sharing a side with a square: a tile can only slide to such a square
    def next_to(cell):
        i, j = cell
        return [(i + di, j + dj) for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1))
                if 0 <= i + di < dim and 0 <= j + dj < dim]

    for t in range(n_steps - 1):
        # slide[(a, b)] = 1 if the tile on square a slides to the empty square b between step
        # t and step t + 1. Exactly one tile slides, since the board must change and only the
        # empty square can move. The slide is tied to the empty square before and after it by
        # sums: the empty square at b before the step receives one tile, and the empty square
        # at a after the step is where that tile came from. slide is continuous: once the empty
        # squares are 0/1 the sums leave a single slide with value 1.
        slide = {(a, b): pulp.LpVariable(f"slide_{t}_{a[0]}_{a[1]}_{b[0]}_{b[1]}", 0, 1)
                 for b in cells for a in next_to(b)}
        for b in cells:
            problem += pulp.lpSum(slide[(a, b)] for a in next_to(b)) == board[t][(b, 0)]
        for a in cells:
            problem += pulp.lpSum(slide[(a, b)] for b in next_to(a)) == board[t + 1][(a, 0)]

        for v in values:
            if v == 0:
                continue
            # a tile that slides from a to b is on b at the next step
            for (a, b), moved in slide.items():
                problem += board[t + 1][(b, v)] >= board[t][(a, v)] + moved - 1
            # a tile that does not slide stays on its square
            for a in cells:
                problem += board[t + 1][(a, v)] >= board[t][(a, v)] - pulp.lpSum(
                    slide[(a, b)] for b in next_to(a))

    # the board at every step, one number per square
    steps = [[[pulp.lpSum(v * board[t][((i, j), v)] for v in values) for j in range(dim)]
              for i in range(dim)] for t in range(n_steps)]

    return problem, {"steps": steps}
