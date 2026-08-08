# Import libraries
from cpmpy import *
import json

# Parameters
k = 4  # Number of sets
n = 4  # Numbers from 1 to n
total_numbers = k * n  # Total numbers in the sequence

# Decision Variables
solution = intvar(1, n, shape=total_numbers, name="solution")  # The solution sequence

# Model
model = Model()

# Constraint: Each number appears exactly k times in the sequence
for num in range(1, n+1):
    model += sum(solution == num) == k

# Constraint: For each number m, consecutive occurrences are m apart
for m in range(1, n+1):
    for i in range(total_numbers - m - 1):
        model += (solution[i] == m).implies(solution[i+m+1] == m)

# Solve
model.solve()

# Get positions after solving
position = []
for num in range(1, n+1):
    pos = [i+1 for i in range(total_numbers) if solution.value()[i] == num]
    position.extend(pos)

# Print solution
solution_dict = {
    "position": position,
    "solution": solution.value().tolist()
}
print(json.dumps(solution_dict))
# End of CPMPy script