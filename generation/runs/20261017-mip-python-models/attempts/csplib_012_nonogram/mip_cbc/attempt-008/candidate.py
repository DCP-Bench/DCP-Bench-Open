# Nonogram (csplib 012): shade squares of a rows x cols grid so that every row and
# every column reads as its given sequence of blocks of consecutive shaded squares.
# Output board[i][j] is 1 for a shaded square and 0 otherwise.
# Zero entries in a rule are padding and carry no block.
import mip


def line_windows(n, lengths, known):
    # For each block of one line, the start squares at which it can sit in some
    # arrangement of the whole line that agrees with the squares already known.
    # known[j] is 0, 1 or None. Blocks in order, at least one 0 between blocks.
    k = len(lengths)
    c0 = [0] * (n + 1)
    c1 = [0] * (n + 1)
    for j in range(n):
        c0[j + 1] = c0[j] + (known[j] == 0)
        c1[j + 1] = c1[j] + (known[j] == 1)

    def zeros_ok(a, b):  # the squares in [a, b) can all be unshaded
        return c1[b] - c1[a] == 0

    def ones_ok(a, b):  # the squares in [a, b) can all be shaded
        return c0[b] - c0[a] == 0

    # Forward: ends[t] holds the squares just after block t-1 in some valid prefix.
    ends = [{0}]
    fwd = []
    for t in range(k):
        length = lengths[t]
        gap = 1 if t > 0 else 0
        starts = set()
        nxt = set()
        for e in ends[t]:
            for s in range(e + gap, n - length + 1):
                if not zeros_ok(e, s):
                    break
                if ones_ok(s, s + length):
                    starts.add(s)
                    nxt.add(s + length)
        fwd.append(starts)
        ends.append(nxt)

    # Backward: bwd[t] holds the starts of block t for which blocks t.. fit after it.
    bwd = [set()] * k
    for t in reversed(range(k)):
        length = lengths[t]
        starts = set()
        for s in range(0, n - length + 1):
            if not ones_ok(s, s + length):
                continue
            e = s + length
            if t == k - 1:
                if zeros_ok(e, n):
                    starts.add(s)
            else:
                for b in sorted(bwd[t + 1]):
                    if b < e + 1:
                        continue
                    if not zeros_ok(e, b):
                        break
                    starts.add(s)
                    break
        bwd[t] = starts

    return [sorted(fwd[t] & bwd[t]) for t in range(k)]


def propagate(n, lengths, known):
    # Squares every arrangement agrees on: a block covering all its possible starts
    # shades the squares they share, and a square no block can reach is unshaded.
    # Returns the squares it fixes as {index: value}.
    windows = line_windows(n, lengths, known)
    fixed = {}
    coverable = [False] * n
    for t, length in enumerate(lengths):
        starts = windows[t]
        if not starts:
            continue
        for j in range(starts[-1], starts[0] + length):
            fixed[j] = 1
        for s in starts:
            for j in range(s, s + length):
                coverable[j] = True
    for j in range(n):
        if not coverable[j]:
            fixed[j] = 0
    return {j: v for j, v in fixed.items() if known[j] is None}


def build(instance):
    rows = instance["rows"]
    cols = instance["cols"]
    row_rules = instance["row_rules"]
    col_rules = instance["col_rules"]

    row_len = [[v for v in row_rules[i] if v > 0] for i in range(rows)]
    col_len = [[v for v in col_rules[j] if v > 0] for j in range(cols)]

    # Squares fixed by propagating the clues line by line, until nothing changes.
    known = [[None] * cols for _ in range(rows)]
    changed = True
    while changed:
        changed = False
        for i in range(rows):
            for j, v in propagate(cols, row_len[i], known[i]).items():
                known[i][j] = v
                changed = True
        for j in range(cols):
            column = [known[i][j] for i in range(rows)]
            for i, v in propagate(rows, col_len[j], column).items():
                known[i][j] = v
                changed = True

    m = mip.Model(solver_name="CBC")
    x = [
        [m.add_var(f"x_{i}_{j}", var_type=mip.BINARY) for j in range(cols)]
        for i in range(rows)
    ]

    def add_line(cells, lengths, windows, tag):
        k = len(lengths)
        # start[t][s] is 1 when block t starts at square s, for the squares s where
        # block t can start at all (windows).
        start = []
        for t in range(k):
            st = {}
            for s in windows[t]:
                st[s] = m.add_var(f"{tag}_st{t}_{s}", var_type=mip.BINARY)
            m.add_constr(mip.xsum(st.values()) == 1)
            start.append(st)

        # Blocks appear in the order given by the description, separated by gaps of
        # unspecified size (at least one unshaded square between two blocks). Block t+1
        # may start at square s only if block t starts at least length_t + 1 squares before.
        for t in range(k - 1):
            for s, b in start[t + 1].items():
                prev = mip.xsum(
                    start[t][q] for q in start[t] if q <= s - lengths[t] - 1
                )
                m.add_constr(b <= prev)

        # The squares of the line are shaded exactly where a block covers them.
        for j, cell in enumerate(cells):
            terms = []
            for t, length in enumerate(lengths):
                terms.extend(
                    start[t][q] for q in start[t] if j - length + 1 <= q <= j
                )
            m.add_constr(cell == mip.xsum(terms))

        # The shaded squares of the line add up to the sum of its block lengths.
        m.add_constr(mip.xsum(cells) == sum(lengths))

    # Constraints for each row: the sequence of shaded blocks given for the row.
    for i in range(rows):
        add_line(x[i], row_len[i], line_windows(cols, row_len[i], known[i]), f"r{i}")

    # Constraints for each column: the sequence of shaded blocks given for the column.
    for j in range(cols):
        column = [known[i][j] for i in range(rows)]
        add_line(
            [x[i][j] for i in range(rows)],
            col_len[j],
            line_windows(rows, col_len[j], column),
            f"c{j}",
        )

    # Squares fixed by the propagation.
    for i in range(rows):
        for j in range(cols):
            if known[i][j] is not None:
                m.add_constr(x[i][j] == known[i][j])

    # No objective: the model is a satisfaction problem.
    board = [[x[i][j] for j in range(cols)] for i in range(rows)]
    return m, {"board": board}
