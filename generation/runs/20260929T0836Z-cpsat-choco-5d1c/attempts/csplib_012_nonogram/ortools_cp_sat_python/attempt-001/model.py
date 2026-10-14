# Nonogram: shade cells of a grid so that in every row and column the blocks of
# consecutive shaded cells have exactly the lengths listed in its rule, in
# order, separated by at least one empty cell. A rule padded with 0s ignores the
# 0 entries.
from ortools.sat.python import cp_model


def line_automaton(rule):
    """Finite automaton that accepts exactly the lines (0 = empty, 1 = shaded) matching the rule.

    States count how much of the rule has been read: inside a block the state
    advances by one per shaded cell, and after a block one empty cell is needed.
    """
    blocks = [length for length in rule if length > 0]
    transitions = []
    state = 0
    for length in blocks:
        transitions.append((state, 0, state))  # empty cells before the block
        for _ in range(length):
            transitions.append((state, 1, state + 1))  # one more shaded cell of the block
            state += 1
        transitions.append((state, 0, state + 1))  # the empty cell that ends the block
        state += 1
    transitions.append((state, 0, state))  # empty cells after the last block
    # the line may end right after the last block or after the empty cells that follow it
    accepting = [s for s in (state - 1, state) if s >= 0]
    return transitions, accepting


def build(instance):
    row_rules = instance["row_rules"]
    col_rules = instance["col_rules"]
    n_rows, n_cols = len(row_rules), len(col_rules)

    model = cp_model.CpModel()

    # board[r][c] = 1 when the cell is shaded, 0 when it is empty
    board = [[model.new_int_var(0, 1, f"board_{r}_{c}") for c in range(n_cols)] for r in range(n_rows)]

    # each row follows its rule
    for r, rule in enumerate(row_rules):
        transitions, accepting = line_automaton(rule)
        model.add_automaton(board[r], 0, accepting, transitions)
    # each column follows its rule
    for c, rule in enumerate(col_rules):
        transitions, accepting = line_automaton(rule)
        model.add_automaton([board[r][c] for r in range(n_rows)], 0, accepting, transitions)

    return model, {"board": board}
