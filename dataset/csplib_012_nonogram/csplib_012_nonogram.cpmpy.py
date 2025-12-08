#!/usr/bin/python3
# Category: csplib
# Source and problem instances: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob012_nonogram.py
# Source description: https://www.csplib.org/Problems/prob012/

"""
Nonograms are a popular puzzle, which goes by different names in different countries. Solvers have to shade in squares
in a grid so that blocks of consecutive shaded squares satisfy constraints given for each row and column. Constraints
typically indicate the sequence of shaded blocks (e.g. 3,1,2 means that there is a block of 3, then a gap of unspecified
size, a block of length 1, another gap, and then a block of length 2).

Print the solution board (board) as a list of lists of integers, where 1 represents a shaded square and 0 represents an unshaded square.
"""

# Data
rows = 8  # Number of rows
row_rule_len = 2  # Maximum length of row rules
row_rules = [
    [0, 1],
    [0, 2],
    [4, 4],
    [0, 12],
    [0, 8],
    [0, 9],
    [3, 4],
    [2, 2]
]  # Rules for rows
cols = 13  # Number of columns
col_rule_len = 2  # Maximum length of column rules
col_rules = [
    [0, 2],
    [2, 1],
    [3, 2],
    [0, 6],
    [1, 4],
    [0, 3],
    [0, 4],
    [0, 4],
    [0, 4],
    [0, 5],
    [0, 4],
    [1, 3],
    [0, 2]
]  # Rules for columns
# End of data

# Import libraries
import json
from cpmpy import *


def nonogram(row_rules, col_rules, **kwargs):
    solver = SolverLookup.get("ortools")
    n_rows, n_cols = len(row_rules), len(col_rules)
    board = intvar(0, 1, shape=(n_rows, n_cols), name="board")
    solver.user_vars.update(set(board.flatten()))

    # Patterns of each row must be correct
    for r, pattern in enumerate(row_rules):
        automaton_func, final_states = transition_function(pattern)
        solver.ort_model.AddAutomaton(
            solver.solver_vars(board[r]),
            starting_state=0, final_states=final_states,
            transition_triples=automaton_func
        )

    # Patterns of each column must be correct
    for c, pattern in enumerate(col_rules):
        automaton_func, final_states = transition_function(pattern)
        solver.ort_model.AddAutomaton(
            solver.solver_vars(board[:, c]),
            starting_state=0, final_states=final_states,
            transition_triples=automaton_func
        )

    return solver, (board,)


def transition_function(pattern):
    """
    Pattern is a vector containing the lengths of blocks with value 1
    """
    func = []
    n_states = 0
    for block_length in pattern:
        if block_length == 0:
            continue
        func += [(n_states, 0, n_states)]
        for _ in range(block_length):
            func += [(n_states, 1, n_states + 1)]
            n_states += 1

        func += [(n_states, 0, n_states + 1)]
        n_states += 1

    func += [(n_states, 0, n_states)]
    # Line can end with 0 or 1
    return func, [n_states - 1, n_states]


# Example usage
model, (board,) = nonogram(row_rules, col_rules)

# Solve
model.solve()

# Print
solution = {"board": board.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
