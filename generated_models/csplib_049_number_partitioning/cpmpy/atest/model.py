from cpmpy import *
import json

# Parameters
n = 12  # The number N

# Decision variables
# We will use a binary variable to indicate which set each number belongs to
# 0 for set B, 1 for set A
assignment = boolvar(shape=n, name="assignment")

# The numbers 1 to n
numbers = list(range(1, n + 1))

# Model
model = Model()

# A and B have the same cardinality
model += [sum(assignment) == n // 2]

# Sum of numbers in A = sum of numbers in B
model += [sum(assignment * numbers) == sum((1 - assignment) * numbers)]

# Sum of squares of numbers in A = sum of squares of numbers in B
squares = [x**2 for x in numbers]
model += [sum(assignment * squares) == sum((1 - assignment) * squares)]

# Solve the model
model.solve()

# Extract the sets A and B
A = [numbers[i] for i in range(n) if assignment[i].value() == 1]
B = [numbers[i] for i in range(n) if assignment[i].value() == 0]

# Print the solution
solution = {"A": A, "B": B}
print(json.dumps(solution))