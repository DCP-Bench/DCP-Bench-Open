# Import libraries
from cpmpy import *
import json

# Parameters
n = 10  # Size of the chessboard and number of queens

# Decision Variables
queens = intvar(1, n, shape=n, name="queens")  # Position of queens in each row (1-based indexing)

# Model
model = Model()

# Constraint: all queens must be on different columns (implicit by array index)
# Constraint: no two queens can be on the same row
model += AllDifferent(queens)

# Constraint: no two queens can be on the same diagonal
for i in range(n):
    for j in range(i+1, n):
        model += (queens[i] - queens[j] != i - j)  # Diagonal \
        model += (queens[i] - queens[j] != j - i)  # Diagonal /

# Solve
model.solve()

# Print solution
solution = {
    "queens": queens.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script