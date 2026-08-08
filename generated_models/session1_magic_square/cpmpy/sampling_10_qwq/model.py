
import cpmpy as cp
import json

model = cp.Model()

# Decision Variables
square = cp.intvar(1, 16, shape=(4,4), name="square")

# Constraints
# All elements must be distinct
model += cp.AllDifferent(square.flat)

# Each row must sum to 34
for row in square:
    model += cp.sum(row) == 34

# Each column must sum to 34
for col in range(4):
    model += cp.sum(square[:, col]) == 34

# Diagonals must also sum to 34
model += (square[0,0] + square[1,1] + square[2,2] + square[3,3] == 34)
model += (square[0,3] + square[1,2] + square[2,1] + square[3,0] == 34)

# Solve and print
if model.solve():
    solution = {'square': square.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
