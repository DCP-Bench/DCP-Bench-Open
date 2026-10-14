# Nonogram: shade squares of a grid so that, in every row and column, the
# blocks of consecutive shaded squares have exactly the lengths listed in
# that line's rule, in that order, with at least one blank between blocks.
from hermax.model import Model


def line_automaton(blocks):
    """Finite automaton that accepts the lines (0/1 strings) obeying a rule.

    State q counts progress through the rule: each block of length b uses b
    states for its shaded squares and one more for the compulsory blank after
    it. Returns (transitions, accepting), transitions[(q, v)] = next state.
    """
    transitions = {}
    state = 0
    for b in blocks:
        transitions[(state, 0)] = state  # blanks before the block
        for _ in range(b):
            transitions[(state, 1)] = state + 1  # one more shaded square
            state += 1
        transitions[(state, 0)] = state + 1  # the blank that ends the block
        state += 1
    transitions[(state, 0)] = state  # blanks after the last block
    # the line may end right after the last block or after trailing blanks
    accepting = {state} if not blocks else {state - 1, state}
    return transitions, accepting


def post_line_rule(m, cells, blocks, tag):
    """Constrain the 0/1 variables `cells` to obey the rule `blocks`.

    The automaton is unrolled over the line: at every position exactly one
    automaton state holds. A SAT-based solver has no built-in regular
    constraint, so the unrolled form is used. States that cannot be reached
    from the start, or cannot still reach an accepting state in the squares
    that remain, are never created; this keeps long lines small.
    """
    length = len(cells)
    transitions, accepting = line_automaton(blocks)

    reachable = [{0}]
    for _ in range(length):
        reachable.append({transitions[(q, v)] for q in reachable[-1] for v in (0, 1)
                          if (q, v) in transitions})
    useful = [None] * length + [accepting]
    for i in range(length - 1, -1, -1):
        useful[i] = {q for (q, v), nxt in transitions.items() if nxt in useful[i + 1]}
    live = [sorted(reachable[i] & useful[i]) for i in range(length + 1)]

    if not live[0]:
        # the rule needs more squares than the line has: no solution
        flag = m.bool(f"{tag}_impossible")
        m &= flag
        m &= ~flag
        return

    # holds[i][q]: after the first i squares of the line the automaton is in state q
    holds = []
    for i in range(length + 1):
        states = m.bool_vector(f"{tag}_state{i}", len(live[i]))
        m &= states.exactly_one()
        holds.append({q: states[k] for k, q in enumerate(live[i])})
    m &= holds[0][0]

    for i in range(length):
        for q in live[i]:
            for v in (0, 1):
                nxt = transitions.get((q, v))
                if nxt is not None and nxt in holds[i + 1]:
                    # reading square i with value v moves the automaton from q to nxt
                    m &= (~holds[i][q] | ~(cells[i] == v) | holds[i + 1][nxt])
                else:
                    # no way to continue: this state cannot read value v here
                    m &= (~holds[i][q] | ~(cells[i] == v))


def build(instance):
    row_rules = instance["row_rules"]  # lengths of the blocks of each row, in order
    col_rules = instance["col_rules"]  # lengths of the blocks of each column, in order
    n_rows, n_cols = len(row_rules), len(col_rules)

    m = Model()
    # board[r][c] = 1 if the square is shaded, 0 if it is blank
    board = m.int_matrix("board", n_rows, n_cols, 0, 1)

    # Rules are padded with zeros, which are not blocks, so they are dropped.
    # the blocks of each row must match its rule
    for r, rule in enumerate(row_rules):
        post_line_rule(m, [board[r][c] for c in range(n_cols)], [b for b in rule if b > 0], f"row{r}")

    # the blocks of each column must match its rule
    for c, rule in enumerate(col_rules):
        post_line_rule(m, [board[r][c] for r in range(n_rows)], [b for b in rule if b > 0], f"col{c}")

    return m, {"board": board}
