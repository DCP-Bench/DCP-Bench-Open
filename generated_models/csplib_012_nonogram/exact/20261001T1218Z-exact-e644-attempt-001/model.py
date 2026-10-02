# Nonogram: shade cells of a grid so that the blocks of consecutive shaded cells in every row
# and every column have exactly the lengths listed in that line's rule, in that order.
from exact import Exact


def build(instance):
    row_rules = instance["row_rules"]  # block lengths per row; 0 entries are padding
    col_rules = instance["col_rules"]  # block lengths per column; 0 entries are padding
    n_rows = len(row_rules)
    n_cols = len(col_rules)

    solver = Exact()

    # board[r][c] = 1 when the square in row r, column c is shaded
    board = [[f"board_{r}_{c}" for c in range(n_cols)] for r in range(n_rows)]
    for r in range(n_rows):
        for c in range(n_cols):
            solver.addVariable(board[r][c], 0, 1)

    def post_rule(label, cells, rule):
        """The shaded cells of one line must form the blocks of `rule`, in order.

        Exact has no regular/automaton constraint, so each block j gets one 0/1 indicator
        per possible start position. Block j can start no earlier than after the blocks
        before it with one gap each, and no later than leaving room for the blocks after it;
        the difference between those two bounds is the line's slack, and a block's start is
        its earliest start plus an offset k in 0..slack.
        """
        blocks = [b for b in rule if b > 0]  # zeros are padding, not blocks
        if not blocks:
            # an empty rule means no square of the line is shaded
            solver.addConstraint([(1, cell) for cell in cells], True, 0, True, 0)
            return
        n = len(cells)
        slack = n - (sum(blocks) + len(blocks) - 1)
        earliest = []
        position = 0
        for b in blocks:
            earliest.append(position)
            position += b + 1  # the block plus the gap that must follow it

        starts = [[f"{label}_block_{j}_offset_{k}" for k in range(slack + 1)]
                  for j in range(len(blocks))]
        for j in range(len(blocks)):
            for name in starts[j]:
                solver.addVariable(name, 0, 1)
            # every block starts at exactly one position
            solver.addConstraint([(1, name) for name in starts[j]], True, 1, True, 1)
        # blocks keep their order with a gap in between: the offset of the next block is not
        # smaller than the offset of this one (the gap is already in the earliest starts)
        for j in range(len(blocks) - 1 if slack > 0 else 0):  # with no slack the starts are fixed
            solver.addConstraint([(k, starts[j + 1][k]) for k in range(1, slack + 1)]
                                 + [(-k, starts[j][k]) for k in range(1, slack + 1)], True, 0)
        # a cell is shaded exactly when some block covers it: a block of length b that starts
        # at position s covers the cells s .. s+b-1
        for i in range(n):
            covering = []
            for j, b in enumerate(blocks):
                for k in range(slack + 1):
                    start = earliest[j] + k
                    if start <= i <= start + b - 1:
                        covering.append(starts[j][k])
            solver.addConstraint([(1, cells[i])] + [(-1, name) for name in covering], True, 0, True, 0)

    # the blocks of every row follow the row's rule
    for r in range(n_rows):
        post_rule(f"row_{r}", board[r], row_rules[r])
    # the blocks of every column follow the column's rule
    for c in range(n_cols):
        post_rule(f"col_{c}", [board[r][c] for r in range(n_rows)], col_rules[c])

    return solver, {"board": board}
