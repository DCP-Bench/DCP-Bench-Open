# Nonogram: shade squares of a grid so that the blocks of consecutive shaded squares
# in every row and column have the lengths, in the order, that the rules give.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def add_line(cnf, pool, cells, rule, key):
    """Constrain a line of 0/1 cells (given as literals, true = shaded) to show the
    blocks of `rule` in order, separated by at least one unshaded square.
    Zero entries of a rule are padding and carry no block.

    The line is read left to right by a finite automaton: after each square the
    automaton is in exactly one state. In a state "gap" it is before a block or
    between blocks and may read unshaded squares; in a state "inside a block of
    length L, j squares seen" it must read a shaded square until the block is full,
    and then an unshaded one. The line may end right after the last block or after
    unshaded squares following it. A state variable is true exactly when the
    automaton is in that state, so each variable is the equivalence
    "previous state AND the square read"; that makes the states a function of the
    squares (a plain implication would let the solver invent a state)."""
    blocks = [length for length in rule if length > 0]
    n = len(cells)

    # delta[(state, bit)] = next state. State 0 is the gap before the first block.
    delta = {}
    state = 0
    for length in blocks:
        delta[(state, 0)] = state              # unshaded squares before the block
        for _ in range(length):
            delta[(state, 1)] = state + 1      # one more shaded square of the block
            state += 1
        delta[(state, 0)] = state + 1          # block is full: a gap square follows
        state += 1
    delta[(state, 0)] = state                  # unshaded squares after the last block
    finals = {state - 1, state} if blocks else {state}

    # Keep only states that can be reached from the start and still reach an
    # accepting state in the squares that remain (the automaton has few useful states).
    reach = [{0}]
    for _ in range(n):
        reach.append({delta[(s, b)] for s in reach[-1] for b in (0, 1) if (s, b) in delta})
    alive = [set() for _ in range(n + 1)]
    alive[n] = reach[n] & finals
    for i in range(n - 1, -1, -1):
        alive[i] = {s for s in reach[i]
                    if any(delta.get((s, b)) in alive[i + 1] for b in (0, 1))}
    if 0 not in alive[0]:
        cnf.append([])                         # the rule cannot fit in this line
        return

    var = [{s: pool.id((key, i, s)) for s in alive[i]} for i in range(n + 1)]
    cnf.append([var[0][0]])                    # the automaton starts in state 0
    for i in range(n):
        for target, now in var[i + 1].items():
            sources = [(s, b) for s in alive[i] for b in (0, 1) if delta.get((s, b)) == target]
            bit = sources[0][1]                # every transition into a state reads the same bit
            square = cells[i] if bit == 1 else -cells[i]
            cnf.append([-now, square])
            cnf.append([-now] + [var[i][s] for s, _ in sources])
            for s, _ in sources:
                cnf.append([-var[i][s], -square, now])
    for i in range(1, n + 1):
        cnf.append(list(var[i].values()))      # the automaton never gets stuck


def build(instance):
    row_rules = instance["row_rules"]
    col_rules = instance["col_rules"]
    n_rows, n_cols = len(row_rules), len(col_rules)

    pool = IDPool()
    # board[r][c] = 1 if the square is shaded, 0 if not (0/1 integers, as the brief declares)
    board = [[Integer(f"board{r}_{c}", 0, 1, vpool=pool) for c in range(n_cols)]
             for r in range(n_rows)]
    engine = IntegerEngine(vars=[cell for row in board for cell in row], vpool=pool)
    cnf = engine.clausify()
    shaded = [[board[r][c].equals(1) for c in range(n_cols)] for r in range(n_rows)]

    # the blocks of every row match the row rule
    for r in range(n_rows):
        add_line(cnf, pool, shaded[r], row_rules[r], ("row", r))
    # the blocks of every column match the column rule
    for c in range(n_cols):
        add_line(cnf, pool, [shaded[r][c] for r in range(n_rows)], col_rules[c], ("col", c))

    return cnf, {"board": board}
