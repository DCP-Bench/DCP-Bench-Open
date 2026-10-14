"""Nonogram: shade squares of a grid so that every row and every column shows
its clue, the lengths of its blocks of consecutive shaded squares in order.

Blocks of one line are separated by at least one unshaded square; the gaps
before, between and after them have any size. A zero in a clue is padding.
"""
import pulp


def post_clue(problem, cells, clue, name):
    """The shaded squares of this line form exactly the blocks of the clue, in order.

    Each block gets one 0/1 variable per position where it may start, and
    exactly one of them is on. Choosing the start positions rather than
    constraining the squares directly keeps the LP relaxation tight: a square
    is shaded exactly when some block covers it.
    """
    blocks = [length for length in clue if length > 0]  # zeros are padding
    size = len(cells)
    if not blocks:
        # empty clue: nothing in this line is shaded
        for cell in cells:
            problem += cell == 0
        return

    # earliest start of block k: all blocks before it, each followed by a gap;
    # latest start: all blocks after it, each preceded by a gap, still fit.
    earliest, latest = [], []
    used = 0
    for length in blocks:
        earliest.append(used)
        used += length + 1
    used = 0
    for length in reversed(blocks):
        latest.append(size - used - length)
        used += length + 1
    latest.reverse()

    # start[k][p] = 1 if block k begins at position p
    start = [{p: pulp.LpVariable(f"{name}_b{k}_{p}", cat="Binary")
              for p in range(earliest[k], latest[k] + 1)} for k in range(len(blocks))]

    # every block of the clue is placed exactly once
    for k in range(len(blocks)):
        problem += pulp.lpSum(start[k].values()) == 1

    # block k+1 starts after block k has ended and left one unshaded square:
    # if block k+1 starts at or before p, block k started at or before p - length - 1
    for k in range(len(blocks) - 1):
        for p in start[k + 1]:
            behind = [q for q in start[k] if q <= p - blocks[k] - 1]
            problem += (pulp.lpSum(start[k + 1][q] for q in start[k + 1] if q <= p)
                        <= pulp.lpSum(start[k][q] for q in behind))

    # a square is shaded exactly when one of the blocks covers it
    for position in range(size):
        problem += cells[position] == pulp.lpSum(
            start[k][p]
            for k in range(len(blocks))
            for p in range(max(earliest[k], position - blocks[k] + 1),
                           min(latest[k], position) + 1))


def build(instance):
    row_rules = instance["row_rules"]
    col_rules = instance["col_rules"]
    n_rows, n_cols = instance["rows"], instance["cols"]

    problem = pulp.LpProblem("nonogram", pulp.LpMinimize)

    # board[r][c] = 1 if the square in row r and column c is shaded (declared output)
    board = [[pulp.LpVariable(f"board_{r}_{c}", cat="Binary") for c in range(n_cols)]
             for r in range(n_rows)]

    # the shaded squares of each row follow the row's clue
    for r in range(n_rows):
        post_clue(problem, board[r], row_rules[r], f"row{r}")

    # the shaded squares of each column follow the column's clue
    for c in range(n_cols):
        post_clue(problem, [board[r][c] for r in range(n_rows)], col_rules[c], f"col{c}")

    return problem, {"board": board}
