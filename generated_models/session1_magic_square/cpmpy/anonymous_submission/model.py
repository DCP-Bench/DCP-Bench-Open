from cpmpy import *
import json
import numpy as np

# Parameters
n = 4  # Size of the magic square
magic_sum = n * (n**2 + 1) // 2  # Magic constant

# Decision Variables
square = intvar(1, n**2, shape=(n,n), name="square")

# Model
model = Model()

# Constraint: All numbers must be different
model += AllDifferent(square)

# Constraint: Rows must sum to magic_sum
for row in square:
    model += sum(row) == magic_sum

# Constraint: Columns must sum to magic_sum
for col in square.T:  # Transpose to get columns
    model += sum(col) == magic_sum

# Constraint: Diagonals must sum to magic_sum
model += sum(square[i,i] for i in range(n)) == magic_sum  # Main diagonal
model += sum(square[i,n-1-i] for i in range(n)) == magic_sum  # Anti-diagonal

# Solve
model.solve()

# Print solution
solution = {"square": np.array(square.value()).tolist()}
print(json.dumps(solution))
# End of CPMPy script