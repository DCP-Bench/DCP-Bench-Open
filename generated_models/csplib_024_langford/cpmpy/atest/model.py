# Import libraries
from cpmpy import *
import json

# Parameters
k = 4  # Number of sets
n = 4  # Numbers from 1 to n
total_length = k * n  # Total length of the sequence

# Decision variables
solution = intvar(1, n, shape=total_length, name="solution")  # The sequence of numbers

# Model
model = Model()

# Each number from 1 to n must appear exactly k times in the solution
for i in range(1, n + 1):
    model += [sum(solution == i) == k]

# For each number i, the positions of its occurrences must be i numbers apart
for i in range(1, n + 1):
    # Find the indices where the number i appears in the solution
    indices = [intvar(0, total_length - 1, name=f"pos_{i}_{j}") for j in range(k)]
    model += [AllDifferent(indices)]
    for j in range(k):
        model += [solution[indices[j]] == i]

    # Enforce the required spacing between occurrences of i
    for j in range(1, k):
        model += [indices[j] == indices[j - 1] + i + 1]

# Solve the model
model.solve()

# Compute the positions of each number
position = [[0] * k for _ in range(n)]
for i in range(1, n + 1):
    count = 0
    for idx in range(total_length):
        if solution.value()[idx] == i:
            position[i - 1][count] = idx
            count += 1

# Print the solution
solution_dict = {
    "position": position,
    "solution": solution.value().tolist()
}
print(json.dumps(solution_dict))