
import cpmpy as cp
import json
import numpy as np

# Data
N = 20  # Number of steps to the solution
puzzle_start = [
    [0, 3, 6],
    [2, 4, 8],
    [1, 7, 5]
]

puzzle_end = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]
# End of data

n_rows = len(puzzle_start)
n_cols = len(puzzle_start[0])
size = n_rows * n_cols

# Flatten start and end states for easier handling
start_flat = [puzzle_start[i][j] for i in range(n_rows) for j in range(n_cols)]
end_flat = [puzzle_end[i][j] for i in range(n_rows) for j in range(n_cols)]

model = cp.Model()

# Variables: state of the puzzle at each step (N+1 states including start)
# Each state is a flattened array of size elements with values 0..8 (tiles)
states = cp.intvar(0, size - 1, shape=(N+1, size), name="states")

# Constraints:

# 1) Initial and final states
model += (states[0] == start_flat)
model += (states[N] == end_flat)

# 2) Each state is a permutation of the tiles 0..8 (all tiles present exactly once)
for t in range(N+1):
    model += cp.AllDifferent(states[t])

# 3) Moves: from one state to the next, exactly one tile moves into the empty space by sliding
# Identify position of 0 (empty) in state[t] and state[t+1]
# The difference between states[t] and states[t+1] is one move of one tile adjacent to empty

# Precompute adjacency on the grid: for each position index, which positions are neighbors
neighbors = []
for pos in range(size):
    r, c = divmod(pos, n_cols)
    adj = []
    if r > 0:
        adj.append((r-1)*n_cols + c)
    if r < n_rows-1:
        adj.append((r+1)*n_cols + c)
    if c > 0:
        adj.append(r*n_cols + (c-1))
    if c < n_cols-1:
        adj.append(r*n_cols + (c+1))
    neighbors.append(adj)

for t in range(N):
    # Find empty position in state t and t+1
    empty_pos_t = cp.intvar(0, size-1, name=f"empty_pos_t_{t}")
    empty_pos_t1 = cp.intvar(0, size-1, name=f"empty_pos_t1_{t}")
    model += (cp.Element(states[t], empty_pos_t) == 0)
    model += (cp.Element(states[t+1], empty_pos_t1) == 0)

    # The empty tile moves to where a neighbor tile was, so empty_pos_t1 is neighbor of empty_pos_t
    # So empty_pos_t1 in neighbors[empty_pos_t]
    # We cannot directly index neighbors with variable, so we create constraints:
    # empty_pos_t1 must be one of the neighbors of empty_pos_t

    # Create boolean indicators for neighbors of empty_pos_t
    # Since empty_pos_t is variable, we use reified constraints:
    # For each pos p in 0..size-1: (empty_pos_t == p) => (empty_pos_t1 in neighbors[p])
    # We implement that empty_pos_t1 is in the union of neighbors of empty_pos_t

    # This is a tricky constraint; we use a table constraint to represent the allowed pairs (empty_pos_t, empty_pos_t1)
    allowed_pairs = []
    for p in range(size):
        for nb in neighbors[p]:
            allowed_pairs.append([p, nb])
    model += cp.Table([empty_pos_t, empty_pos_t1], allowed_pairs)

    # After the move, the states differ by swapping empty tile and one adjacent tile
    # All other tiles remain the same

    # Constraint: states[t+1][empty_pos_t] == states[t][empty_pos_t1] (tile moved into empty)
    model += (states[t+1][empty_pos_t] == states[t][empty_pos_t1])
    # states[t+1][empty_pos_t1] == 0 (empty tile moved here)
    model += (states[t+1][empty_pos_t1] == 0)

    # For all other positions p different from empty_pos_t and empty_pos_t1: states[t+1][p] == states[t][p]
    for p in range(size):
        if_cond = ((p != empty_pos_t) & (p != empty_pos_t1))
        # Because we cannot use if_cond directly, we add constraint for each p with reified constraints
        # Instead, add constraints as a set:
        # states[t+1][p] == states[t][p] for all p != empty_pos_t and p != empty_pos_t1
        # We can rewrite it as:
        # For all p in 0..size-1:
        # (p != empty_pos_t) & (p != empty_pos_t1) => states[t+1][p] == states[t][p]
        # Implement as:
        # (p == empty_pos_t) OR (p == empty_pos_t1) OR states[t+1][p] == states[t][p]

        # model += ((p == empty_pos_t) | (p == empty_pos_t1) | (states[t+1][p] == states[t][p]))
        # CPMpy requires the use of boolean variables; let's implement this with reified variables
        b1 = (p == empty_pos_t)
        b2 = (p == empty_pos_t1)
        b3 = (states[t+1][p] == states[t][p])
        model += (b1 | b2 | b3)

# Solve and print
if model.solve():
    # Extract solution states for steps 0..N
    steps = []
    for t in range(N+1):
        state_t = states[t].value().tolist()
        matrix = []
        for r in range(n_rows):
            row = state_t[r*n_cols:(r+1)*n_cols]
            matrix.append(row)
        steps.append(matrix)
    solution = {'steps': steps}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
