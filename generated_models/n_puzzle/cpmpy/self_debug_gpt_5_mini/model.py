
import cpmpy as cp
import json

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

# Model definition
model = cp.Model()

# Problem dimensions
R = 3
C = 3
MAX_VAL = R * C - 1  # 0..8

# Decision Variables
# steps[t, r, c] is the value at row r, col c at time step t (0-based indexing for t)
steps = cp.intvar(0, MAX_VAL, shape=(N_STEPS, R, C), name="steps")

# Constraints

# 1) Each step is a permutation of 0..8 (all different)
for t in range(N_STEPS):
    # Flatten the 3x3 grid to 9 variables and enforce AllDifferent
    model += cp.AllDifferent(steps[t].reshape(R * C).tolist())

# 2) Start and end states fixed
for r in range(R):
    for c in range(C):
        model += (steps[0, r, c] == puzzle_start[r][c])
        model += (steps[N_STEPS - 1, r, c] == puzzle_end[r][c])

# 3) Moves: between successive steps exactly one tile (the one adjacent to the empty) moves into the empty cell.
# Enumerate all ordered adjacent moves (from position p to q where q is neighbor of p).
moves = []
for r in range(R):
    for c in range(C):
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C:
                moves.append(((r, c), (nr, nc)))  # ordered: empty at (r,c) moves to (nr,nc)

# For each consecutive pair of steps, enforce exactly one of the allowed ordered moves occurs
for t in range(N_STEPS - 1):
    b_moves = cp.boolvar(shape=len(moves))
    # For each possible ordered move, if b_moves[i] is true then:
    # - in step t the empty (0) is at p
    # - in step t+1 the empty (0) is at q
    # - the tile at q in step t moves to p in step t+1
    # - all other cells remain unchanged
    for i, ((pr, pc), (qr, qc)) in enumerate(moves):
        bi = b_moves[i]
        # empty at p in step t
        model += bi.implies(steps[t, pr, pc] == 0)
        # empty at q in step t+1
        model += bi.implies(steps[t + 1, qr, qc] == 0)
        # the tile at q in step t moves into p in step t+1
        model += bi.implies(steps[t + 1, pr, pc] == steps[t, qr, qc])
        # all other cells remain the same
        for r in range(R):
            for c in range(C):
                if (r, c) != (pr, pc) and (r, c) != (qr, qc):
                    model += bi.implies(steps[t + 1, r, c] == steps[t, r, c])
    # exactly one move happens
    model += (cp.sum(b_moves) == 1)

# Objective: none (we are given the number of steps and must produce a valid sequence)

# Solve and print
if model.solve():
    solution = {'steps': steps.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
