from cpmpy import *
import json

# Parameters
n = 5  # Size of the grid

# Decision variables
x = intvar(1, n * n, shape=(n, n), name="x")

# Model
model = Model([
    AllDifferent(x)  # All numbers from 1 to n^2 must be placed exactly once
])

# Flatten the grid to get positions of each number
positions = intvar(0, n * n - 1, shape=(n * n), name="positions")
for i in range(n):
    for j in range(n):
        model += [positions[x[i, j] - 1] == i * n + j]

# For each number from 1 to n^2 - 1, enforce the movement rules
for k in range(1, n * n):
    pos_prev = positions[k - 1]
    pos_next = positions[k]
    i_prev = pos_prev // n
    j_prev = pos_prev % n
    i_next = pos_next // n
    j_next = pos_next % n

    # Horizontal or vertical move (Movement Type I): distance of 3
    is_horizontal = (i_prev == i_next) & (abs(j_prev - j_next) == 3)
    is_vertical = (j_prev == j_next) & (abs(i_prev - i_next) == 3)
    is_horizontal_or_vertical = is_horizontal | is_vertical

    # Diagonal move (Movement Type II): distance of 2
    is_diagonal = (abs(i_prev - i_next) == 2) & (abs(j_prev - j_next) == 2)

    # Either horizontal/vertical or diagonal move must be true
    model += [is_horizontal_or_vertical | is_diagonal]

# Solve the model
model.solve()

# Print the solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))