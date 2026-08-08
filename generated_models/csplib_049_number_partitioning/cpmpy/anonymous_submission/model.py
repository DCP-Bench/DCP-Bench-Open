# Import libraries
from cpmpy import *
import json

# Parameters
n = 12  # The number N

# Decision Variables
A = boolvar(shape=n, name="A")  # Boolean array indicating if number is in set A
B = boolvar(shape=n, name="B")  # Boolean array indicating if number is in set B

# Model
model = Model()

# Constraint: A and B have the same cardinality
model += sum(A) == sum(B)

# Constraint: Sum of numbers in A = sum of numbers in B
numbers = cpm_array(range(1, n+1))
model += sum(numbers * A) == sum(numbers * B)

# Constraint: Sum of squares of numbers in A = sum of squares of numbers in B
squares = cpm_array([i*i for i in range(1, n+1)])
model += sum(squares * A) == sum(squares * B)

# Constraint: Each number is in exactly one set (A or B)
for i in range(n):
    model += (A[i] + B[i]) == 1

# Solve
model.solve()

# Convert boolean arrays to number lists
A_solution = [i+1 for i in range(n) if A[i].value()]
B_solution = [i+1 for i in range(n) if B[i].value()]

# Print solution
solution = {
    "A": A_solution,
    "B": B_solution
}
print(json.dumps(solution))
# End of CPMPy script