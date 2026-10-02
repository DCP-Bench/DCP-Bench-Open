# Nonogram: shade cells of a grid so that, in every row and column, the shaded
# cells form exactly the blocks listed in that line's rule, in order, with at
# least one unshaded cell between consecutive blocks.
import z3


def build(instance):
    row_rules = instance["row_rules"]  # row_rules[r]: block lengths of row r, in order
    col_rules = instance["col_rules"]  # col_rules[c]: block lengths of column c, in order
    n_rows = len(row_rules)
    n_cols = len(col_rules)

    # board[r][c] = 1 if the cell is shaded, 0 if not.
    board = [[z3.Int(f"board_{r}_{c}") for c in range(n_cols)] for r in range(n_rows)]

    solver = z3.Solver()
    for r in range(n_rows):
        for c in range(n_cols):
            solver.add(board[r][c] >= 0, board[r][c] <= 1)

    def line_matches_rule(cells, rule, name):
        # Entries equal to 0 in a rule are padding (rules are stored with a fixed
        # width), so only the positive entries are blocks.
        blocks = [b for b in rule if b > 0]
        length = len(cells)
        # Encoding: one start position per block. This is much smaller for Z3 than
        # the finite automaton the reference uses, which needs a state per cell offset.
        starts = [z3.Int(f"{name}_start_{j}") for j in range(len(blocks))]
        for j, b in enumerate(blocks):
            solver.add(starts[j] >= 0, starts[j] + b <= length)
            if j > 0:
                # a block starts after the previous one ended, with one unshaded gap
                solver.add(starts[j] >= starts[j - 1] + blocks[j - 1] + 1)
        for i, cell in enumerate(cells):
            # a cell is shaded exactly when it lies inside one of the blocks
            inside = [z3.And(starts[j] <= i, i < starts[j] + b) for j, b in enumerate(blocks)]
            solver.add((cell == 1) == (z3.Or(inside) if inside else z3.BoolVal(False)))

    # Every row shows its blocks in the order and lengths of its rule.
    for r in range(n_rows):
        line_matches_rule(board[r], row_rules[r], f"row{r}")

    # Every column shows its blocks in the order and lengths of its rule.
    for c in range(n_cols):
        line_matches_rule([board[r][c] for r in range(n_rows)], col_rules[c], f"col{c}")

    return solver, {"board": board}
