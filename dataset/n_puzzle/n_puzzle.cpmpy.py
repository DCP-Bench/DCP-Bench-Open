#!/usr/bin/python3
# Category: cpmpy_examples
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/npuzzle.py

"""
The N-Puzzle is a classic sliding puzzle game where the goal is to move tiles on a grid to achieve a specific end
configuration. The puzzle consists of a grid with \( n+1 \) tiles, one of which is empty. The objective is to trace
the steps to the original picture by moving the tiles into their correct positions.

Input includes the start and end state of the puzzle, along with the number of steps to the solution, which includes the start and end states.
Also, "freezing" is not allowed, meaning that the state of the puzzle must change at each step.

Print the state of the puzzle at each step (steps) as a list of exactly N_STEPS integer 2-dimensional matrices, including the start and end states.
"""

# Data
N_STEPS = 13  # Number of steps to the solution, including start and end states
puzzle_start = [  # Start state of the puzzle, 0 represents the empty tile, STEP 1
    [0, 3, 6],
    [2, 4, 8],
    [1, 7, 5]
]

puzzle_end = [  # End state of the puzzle, STEP [N_STEPS]
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]
# End of data

# Import libraries
from cpmpy import *
import json
import numpy as np


def n_puzzle(puzzle_start, puzzle_end, N_STEPS):

    m = Model()

    (dim,dim2) = puzzle_start.shape
    assert (dim == dim2), "puzzle needs square shape"
    n = dim*dim2 - 1  # e.g. an 8-puzzle

    # State of puzzle at every step
    x = intvar(0,n, shape=(N_STEPS,dim,dim), name="x")

    # Start state constraint
    m += (x[0] == puzzle_start)

    # End state constraint
    m += (x[-1] == puzzle_end)

    # define neighbors = allowed moves for the '0'
    def neigh(i,j):
        # same, left,right, down,up, if within bounds
        for (rr, cc) in [(0,0),(-1,0),(1,0),(0,-1),(0,1)]:
            if 0 <= i + rr < dim and 0 <= j + cc < dim:
                yield i + rr, j + cc

    # Transition: define next based on prev + invariants
    def transition(m, prev_x, next_x):
        # for each position, determine its reachability
        for i in range(dim):
            for j in range(dim):
                m += (next_x[i,j] == 0).implies(any(prev_x[r,c] == 0 for r,c in neigh(i,j)))

        # Invariant: in each step, all cells are different
        m += AllDifferent(next_x)

        # Invariant: only the '0' position can move
        m += ((prev_x == 0) | (next_x == 0) | (prev_x == next_x))

        # The board state must change between steps
        m += any(prev_x != next_x)

    # apply transitions (0,1) (1,2) (2,3) ...
    for i in range(1, N_STEPS):
        transition(m, x[i-1], x[i])

    return (m,x)

# Example usage
model, steps = n_puzzle(np.array(puzzle_start), np.array(puzzle_end), N_STEPS)
model.solve()

# Print
solution = {"steps": steps.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script