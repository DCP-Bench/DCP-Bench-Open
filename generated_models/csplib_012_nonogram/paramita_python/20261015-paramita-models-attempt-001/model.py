# Nonogram: shade squares of a rows x cols grid so that every row and column shows
# its blocks of consecutive shaded squares, in order, separated by unshaded squares.
from functools import reduce

from paramita.modelling import Bool, Iff, If


def any_of(xs):
    # disjunction of a non-empty list of expressions
    return reduce(lambda a, b: a | b, xs)


def line_constraints(tag, cells, blocks):
    """Constraints tying the Bool cells of one line to its block lengths.

    cells: the shaded Bools of the line, in order. blocks: the block lengths in
    order (zero padding already removed).
    """
    W = len(cells)
    cons = []
    if not blocks:
        # no blocks: the whole line is unshaded
        cons += [~cells[c] for c in range(W)]
        return cons

    m = len(blocks)
    # start[k][t]: block k starts at position t (one-hot over its valid starts)
    start = []
    for k, L in enumerate(blocks):
        start.append({t: Bool(f"{tag}_start_{k}_{t}") for t in range(W - L + 1)})
    # prefix[k][t]: block k starts at or before position t
    prefix = []
    for k in range(m):
        p = [Bool(f"{tag}_prefix_{k}_{t}") for t in range(W)]
        prefix.append(p)
        for t in range(W):
            parts = []
            if t > 0:
                parts.append(p[t - 1])
            if t in start[k]:
                parts.append(start[k][t])
            if parts:
                cons.append(Iff(p[t], any_of(parts)))
            else:
                cons.append(~p[t])

    # each block starts exactly once
    for k in range(m):
        cons.append(sum(start[k].values()) == 1)

    # blocks keep their order with at least one unshaded square between them:
    # block k+1 starts at t only if block k starts no later than t - len_k - 1
    for k in range(1, m):
        L_prev = blocks[k - 1]
        for t, s in start[k].items():
            u = t - L_prev - 1
            if u >= 0:
                cons.append(If(s, prefix[k - 1][u]))
            else:
                cons.append(~s)

    # a square is shaded exactly when some block covers it;
    # block k covers c when it starts in (c - len_k, c]
    for c in range(W):
        covers = []
        for k, L in enumerate(blocks):
            if c - L >= 0:
                covers.append(prefix[k][c] & ~prefix[k][c - L])
            else:
                covers.append(prefix[k][c])
        cons.append(Iff(cells[c], any_of(covers)))
    return cons


def build(instance):
    R, C = instance["rows"], instance["cols"]
    shade = [[Bool(f"shade_{r}_{c}") for c in range(C)] for r in range(R)]

    cons = []
    # row blocks, in the order given, zero padding skipped
    for r in range(R):
        blocks = [v for v in instance["row_rules"][r] if v > 0]
        cons += line_constraints(f"row{r}", shade[r], blocks)
    # column blocks, in the order given, zero padding skipped
    for c in range(C):
        blocks = [v for v in instance["col_rules"][c] if v > 0]
        cons += line_constraints(f"col{c}", [shade[r][c] for r in range(R)], blocks)

    # board: 1 for a shaded square, 0 for an unshaded one
    board = [[1 * shade[r][c] for c in range(C)] for r in range(R)]
    return cons, {"board": board}
