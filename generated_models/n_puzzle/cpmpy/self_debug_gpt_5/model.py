
import cpmpy as cp
import json

# Data (optional)
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

# Dimensions
H, W = 3, 3
N = H * W  # 9

# Decision Variables
# steps[t][i][j] is the tile at row i, col j at step t
steps = cp.intvar(0, N-1, shape=(N_STEPS, H, W), name="steps")
# Position of the empty tile (0) in flattened indexing [0..8] at each step
pos0 = cp.intvar(0, N-1, shape=N_STEPS, name="pos0")

# Flattened views for convenience: s_flat[t][k] with k in 0..8
s_flat = steps.reshape((N_STEPS, N))

# Constraints

# Start and end states fixed
for i in range(H):
    for j in range(W):
        model += (steps[0, i, j] == puzzle_start[i][j])
        model += (steps[N_STEPS-1, i, j] == puzzle_end[i][j])

# Each state is a permutation of 0..8, and link pos0[t] to location of 0
for t in range(N_STEPS):
    model += cp.AllDifferent(s_flat[t])
    model += (cp.Element(s_flat[t], pos0[t]) == 0)

# Transitions between consecutive steps: one legal slide, no freezing
for t in range(N_STEPS - 1):
    # Exactly one move direction
    b = cp.boolvar(shape=4, name=f"move_{t}")  # [up, down, left, right]
    model += (cp.sum(b) == 1)

    pos = pos0[t]
    posn = pos0[t+1]
    r = pos // W
    c = pos % W

    # Legal adjacency of blank (0)
    # up
    model += b[0].implies(r > 0)
    model += b[0].implies(posn == pos - W)
    # down
    model += b[1].implies(r < H-1)
    model += b[1].implies(posn == pos + W)
    # left
    model += b[2].implies(c > 0)
    model += b[2].implies(posn == pos - 1)
    # right
    model += b[3].implies(c < W-1)
    model += b[3].implies(posn == pos + 1)

    # Swap the 0 with the adjacent tile, others unchanged
    # The tile moving into pos (where 0 was) is the one that was at posn
    model += (cp.Element(s_flat[t+1], pos) == cp.Element(s_flat[t], posn))
    # All other positions remain unchanged
    for k in range(N):
        model += ((pos != k) & (posn != k)).implies(s_flat[t+1, k] == s_flat[t, k])

    # No freezing: state must change
    model += (cp.sum([s_flat[t, k] != s_flat[t+1, k] for k in range(N)]) >= 1)

# Solve and print
if model.solve():
    solution = {'steps': steps.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
