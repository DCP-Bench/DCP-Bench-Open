"""Nonogram: shade squares of a grid so that every row and every column shows
its clue, the lengths of its blocks of consecutive shaded squares in order.

Blocks of one line are separated by at least one unshaded square; the gaps
before, between and after them have any size. A zero in a clue is padding.
"""
import pulp


def post_clue(problem, cells, clue, name):
    """The shaded squares of this line form exactly the blocks of the clue, in order.

    Every block gets an order encoding of its start position: begun[k][p] = 1 if
    block k starts at position p or earlier. Compared with one 0/1 variable per
    start position, the rows linking neighbouring blocks and squares then have
    two or three entries instead of a sum over all earlier positions, which keeps
    the program sparse on long lines.
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

    # begun[k][p] for earliest[k] <= p < latest[k]; before earliest[k] block k
    # cannot have started and from latest[k] on it certainly has.
    begun = [{p: pulp.LpVariable(f"{name}_b{k}_{p}", cat="Binary")
              for p in range(earliest[k], latest[k])} for k in range(len(blocks))]

    def started_by(k, position):
        """Block k starts at `position` or earlier: a variable, or the constant 0 / 1."""
        if position < earliest[k]:
            return 0
        if position >= latest[k]:
            return 1
        return begun[k][position]

    # once block k has started it stays started
    for k in range(len(blocks)):
        for p in range(earliest[k], latest[k] - 1):
            problem += begun[k][p] <= begun[k][p + 1]

    # block k+1 starts after block k has ended and left one unshaded square: if
    # block k+1 has started by p, block k had started by p - length(k) - 1
    for k in range(len(blocks) - 1):
        for p in range(earliest[k + 1], latest[k + 1]):
            problem += begun[k + 1][p] <= started_by(k, p - blocks[k] - 1)

    # a square is shaded exactly when some block covers it: block k covers position
    # c when it has started by c but not yet by c - length(k)
    for c in range(size):
        problem += cells[c] == pulp.lpSum(
            started_by(k, c) - started_by(k, c - blocks[k]) for k in range(len(blocks)))


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
