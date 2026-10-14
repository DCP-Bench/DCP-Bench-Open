"""Nonogram: shade squares of a grid so that each row and column shows the given blocks.

A rule lists the lengths of the blocks of consecutive shaded squares in a line, in order,
with at least one unshaded square between blocks; zeros in a rule are padding.
"""
from docplex.mp.model import Model


def build(instance):
    n_rows = instance["rows"]
    n_cols = instance["cols"]
    row_rules = instance["row_rules"]  # row_rules[r]: block lengths of row r, 0 = padding
    col_rules = instance["col_rules"]  # col_rules[c]: block lengths of column c, 0 = padding

    model = Model("nonogram")

    def place_blocks(rule, size, name):
        """Place the blocks of one line of `size` squares.

        start[b, p] is 1 when block b begins at square p. Returns, for each square,
        the list of those variables whose block would cover it; the square is shaded
        exactly when one of them is 1 (at most one can be, since blocks do not overlap).
        """
        lengths = [length for length in rule if length > 0]
        starts = []
        for b, length in enumerate(lengths):
            # Earliest start: the blocks before it and one gap after each of them.
            # Latest start: the blocks after it and one gap before each of them.
            first = sum(earlier + 1 for earlier in lengths[:b])
            last = size - length - sum(later + 1 for later in lengths[b + 1:])
            start = {p: model.binary_var(name=f"{name}_b{b}_at{p}") for p in range(first, last + 1)}
            # Each block begins at exactly one square.
            model.add_constraint(model.sum(start.values()) == 1)
            starts.append(start)
        # Consecutive blocks are separated by at least one unshaded square: the next
        # block begins at least length + 1 squares after this one.
        for b in range(len(lengths) - 1):
            begin = model.sum(p * v for p, v in starts[b].items())
            next_begin = model.sum(p * v for p, v in starts[b + 1].items())
            model.add_constraint(next_begin - begin >= lengths[b] + 1)
        # Square i is covered by block b when b begins among the `length` squares ending at i.
        return [[v for b, length in enumerate(lengths)
                 for p, v in starts[b].items() if i - length < p <= i]
                for i in range(size)]

    row_view = [place_blocks(row_rules[r], n_cols, f"row{r}") for r in range(n_rows)]
    col_view = [place_blocks(col_rules[c], n_rows, f"col{c}") for c in range(n_cols)]

    # The row view and the column view describe the same board, square by square.
    for r in range(n_rows):
        for c in range(n_cols):
            if row_view[r][c] or col_view[c][r]:
                model.add_constraint(model.sum(row_view[r][c]) == model.sum(col_view[c][r]))

    # The declared output: the board, read from the row view (0 where no block can reach).
    board = [[model.sum(row_view[r][c]) if row_view[r][c] else 0 for c in range(n_cols)]
             for r in range(n_rows)]
    return model, {"board": board}
