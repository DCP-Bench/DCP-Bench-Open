# Problem: Shade the grid so that every row and column shows its block sequence.
from pycsp3 import *


def run_automaton(blocks):
    """Automaton for 0/1 lines whose runs of 1s are exactly the given blocks, in order.

    State g<i>: i blocks are done and the line is in a gap. State r<j>_<l>: block j is
    running with l cells so far. A block must be followed by a 0 before the next starts.
    """
    k = len(blocks)
    transitions = []
    for i in range(k + 1):
        transitions.append((f"g{i}", 0, f"g{i}"))
        if i < k:
            transitions.append((f"g{i}", 1, f"r{i + 1}_1"))
    for j in range(1, k + 1):
        size = blocks[j - 1]
        for l in range(1, size + 1):
            if l < size:
                transitions.append((f"r{j}_{l}", 1, f"r{j}_{l + 1}"))
        transitions.append((f"r{j}_{size}", 0, f"g{j}"))
    final = [f"g{k}"] + ([f"r{k}_{blocks[k - 1]}"] if k > 0 else [])
    return Automaton(start="g0", transitions=transitions, final=final)


def blocks_of(rule):
    # zeros pad the rule to its fixed length
    return [v for v in rule if v > 0]


rows = data.rows
cols = data.cols
# board[r][c] = 1 if the square in row r and column c is shaded
board = VarArray(size=[rows, cols], dom={0, 1})
satisfy(
    # each row shows its block sequence
    [Regular(scope=board[r], automaton=run_automaton(blocks_of(data.row_rules[r]))) for r in range(rows)],
    # each column shows its block sequence
    [Regular(scope=board[:, c], automaton=run_automaton(blocks_of(data.col_rules[c]))) for c in range(cols)],
)
