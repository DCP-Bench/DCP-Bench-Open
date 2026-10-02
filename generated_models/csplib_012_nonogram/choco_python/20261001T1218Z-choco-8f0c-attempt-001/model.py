# Nonogram: shade cells of a grid (1 = shaded, 0 = unshaded) so that the blocks of
# consecutive shaded cells in every row and column match the clue for that line.
from pychoco.model import Model
from pychoco.objects.automaton.finite_automaton import FiniteAutomaton


def line_automaton(clue):
    """Automaton accepting exactly the 0/1 lines whose shaded blocks have the lengths in clue.

    Zero entries of the clue are padding and are skipped; the other entries are the
    block lengths in order. Blocks are separated by at least one unshaded cell, and the
    line may start and end with any number of unshaded cells.
    """
    transitions = []  # (state, symbol, next state)
    n_states = 0
    for block_length in clue:
        if block_length == 0:
            continue
        transitions.append((n_states, 0, n_states))  # unshaded cells before this block
        for _ in range(block_length):  # the shaded cells of this block
            transitions.append((n_states, 1, n_states + 1))
            n_states += 1
        transitions.append((n_states, 0, n_states + 1))  # at least one unshaded cell after it
        n_states += 1
    transitions.append((n_states, 0, n_states))  # unshaded cells after the last block
    # The line may end right after the last block or after the unshaded cells that follow it.
    # With an all-zero clue (no blocks) state 0 is the only state and it accepts the empty line.
    final_states = [state for state in (n_states - 1, n_states) if state >= 0]

    automaton = FiniteAutomaton()
    states = [automaton.add_state() for _ in range(n_states + 1)]
    automaton.set_initial_state(states[0])
    for state in final_states:
        automaton.set_final(states[state])
    for source, symbol, target in transitions:
        automaton.add_transition(states[source], states[target], symbol)
    return automaton


def build(instance):
    row_rules = instance["row_rules"]  # clue of each row (zeros are padding)
    col_rules = instance["col_rules"]  # clue of each column (zeros are padding)
    n_rows, n_cols = len(row_rules), len(col_rules)

    model = Model()

    # board[r][c] = 1 if the cell in row r, column c is shaded
    board = [[model.intvar(0, 1, name=f"board_{r}_{c}") for c in range(n_cols)] for r in range(n_rows)]

    # the blocks of shaded cells in each row match the clue of that row
    for r, clue in enumerate(row_rules):
        model.regular(board[r], line_automaton(clue)).post()

    # the blocks of shaded cells in each column match the clue of that column
    for c, clue in enumerate(col_rules):
        model.regular([board[r][c] for r in range(n_rows)], line_automaton(clue)).post()

    return model, {"board": board}
