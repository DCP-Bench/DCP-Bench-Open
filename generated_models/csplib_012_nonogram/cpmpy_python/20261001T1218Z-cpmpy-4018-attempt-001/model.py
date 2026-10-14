# Nonogram: shade cells of a grid so that in every row and column the blocks of
# consecutive shaded cells have exactly the lengths listed in its rule, in
# order, separated by at least one empty cell. A rule padded with 0s ignores the
# 0 entries.
import cpmpy as cp


def line_automaton(rule):
    """Automaton that accepts exactly the lines (0 = empty, 1 = shaded) matching the rule.

    The state counts how much of the rule has been read: inside a block it advances by
    one per shaded cell, and after a block one empty cell is required before the next.
    Returns (transitions, accepting states); the start state is 0.
    """
    blocks = [length for length in rule if length > 0]  # zeros are padding, not blocks
    transitions = []
    state = 0
    for length in blocks:
        transitions.append((state, 0, state))          # empty cells before the block
        for _ in range(length):
            transitions.append((state, 1, state + 1))  # one more shaded cell of the block
            state += 1
        transitions.append((state, 0, state + 1))      # the empty cell that ends the block
        state += 1
    transitions.append((state, 0, state))              # empty cells after the last block
    # The line may end right after the last block or after the empty cells following it.
    # With no blocks there is no state before the last block, so only state 0 accepts.
    accepting = [s for s in (state - 1, state) if s >= 0]
    return transitions, accepting


def build(instance):
    row_rules = instance["row_rules"]
    col_rules = instance["col_rules"]
    n_rows, n_cols = len(row_rules), len(col_rules)

    # board[r, c] = 1 when the cell is shaded, 0 when it is empty
    board = cp.intvar(0, 1, shape=(n_rows, n_cols), name="board")

    model = cp.Model()

    # Each row shows its shaded blocks in the order and lengths its rule lists.
    for r, rule in enumerate(row_rules):
        transitions, accepting = line_automaton(rule)
        model += cp.Regular(list(board[r, :]), transitions, 0, accepting)

    # Each column shows its shaded blocks in the order and lengths its rule lists.
    for c, rule in enumerate(col_rules):
        transitions, accepting = line_automaton(rule)
        model += cp.Regular(list(board[:, c]), transitions, 0, accepting)

    return model, {"board": board}
