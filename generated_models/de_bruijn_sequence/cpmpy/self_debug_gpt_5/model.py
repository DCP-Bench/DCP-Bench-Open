
import cpmpy as cp
import json

# Data
k = 2
n = 4
L = k ** n  # 16
weights = [8, 4, 2, 1]  # binary weights for 4-bit window
# End of data

# Model definition
model = cp.Model()

# Decision Variables
de_bruijn = cp.intvar(0, 1, shape=L, name="de_bruijn")

# Constraints
# Encode each cyclic 4-bit window as an integer in 0..15 and enforce all are different
windows = [cp.sum([weights[j] * de_bruijn[(i + j) % L] for j in range(n)]) for i in range(L)]
model += cp.AllDifferent(windows)

# Symmetry breaking: fix the first 4 bits to 0 to anchor rotation (place '0000' at position 0)
model += (de_bruijn[0] == 0)
model += (de_bruijn[1] == 0)
model += (de_bruijn[2] == 0)
model += (de_bruijn[3] == 0)

# Solve and print
if model.solve():
    solution = {'de_bruijn': de_bruijn.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
