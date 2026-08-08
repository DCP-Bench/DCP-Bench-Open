from cpmpy import *
import json

# Input data
N = 20  # Number of steps to the solution
puzzle_start = [  # Start state of the puzzle, 0 represents the empty tile
    [0, 3, 6],
    [2, 4, 8],
    [1, 7, 5]
]
puzzle_end = [  # End state of the puzzle
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]

# Grid size
grid_size = len(puzzle_start)

# Decision variables
# steps[t][i][j] represents the tile at position (i, j) in step t
steps = intvar(0, grid_size * grid_size - 1, shape=(N + 1, grid_size, grid_size), name="steps")

# Model
model = Model()

# Constraint: Initial state must be equal to puzzle_start
for i in range(grid_size):
    for j in range(grid_size):
        model += [steps[0, i, j] == puzzle_start[i][j]]

# Constraint: Final state must be equal to puzzle_end
for i in range(grid_size):
    for j in range(grid_size):
        model += [steps[N, i, j] == puzzle_end[i][j]]

# Constraint: Each step must be a valid move from the previous step
for t in range(N):
    # Get the position of the empty tile in step t
    empty_i = intvar(0, grid_size - 1, name=f"empty_i_{t}")
    empty_j = intvar(0, grid_size - 1, name=f"empty_j_{t}")
    model += [steps[t, empty_i, empty_j] == 0]

    # Get the position of the empty tile in step t+1
    empty_i_next = intvar(0, grid_size - 1, name=f"empty_i_next_{t}")
    empty_j_next = intvar(0, grid_size - 1, name=f"empty_j_next_{t}")
    model += [steps[t + 1, empty_i_next, empty_j_next] == 0]

    # The empty tile must move one step in one of the four directions
    model += [(empty_i_next == empty_i + 1) & (empty_j_next == empty_j) |
              (empty_i_next == empty_i - 1) & (empty_j_next == empty_j) |
              (empty_i_next == empty_i) & (empty_j_next == empty_j + 1) |
              (empty_i_next == empty_i) & (empty_j_next == empty_j - 1)]

    # All other tiles must remain the same
    for i in range(grid_size):
        for j in range(grid_size):
            if not ((i == empty_i) & (j == empty_j)) and not ((i == empty_i_next) & (j == empty_j_next)):
                model += [steps[t, i, j] == steps[t + 1, i, j]]

# Constraint: Each step must contain the same set of tiles (excluding the empty tile)
for t in range(N + 1):
    # Flatten the grid and remove the 0 (empty tile)
    tiles = [steps[t, i, j] for i in range(grid_size) for j in range(grid_size) if steps[t, i, j] != 0]
    model += [AllDifferent(tiles)]

# Solve the model
model.solve()

# Print the solution
solution = {"steps": [step.tolist() for step in steps.value()]}
print(json.dumps(solution))