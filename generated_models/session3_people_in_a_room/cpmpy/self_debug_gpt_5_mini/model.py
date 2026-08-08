
import cpmpy as cp
import json

# Data
n = 13
total_females = 9  # represented by 1
total_males = 4    # represented by 0

# Model definition
model = cp.Model()

# Decision Variables
sequence = cp.intvar(0, 1, shape=n, name="sequence")  # 1 = female, 0 = male

# Constraints
# Total counts
model += cp.sum(sequence) == total_females

# For every prefix, the ratio females:males <= 7/3
# i.e., 3 * females_prefix <= 7 * males_prefix
for k in range(1, n + 1):
    females_prefix = cp.sum(sequence[:k])
    males_prefix = k - females_prefix
    model += females_prefix * 3 <= 7 * males_prefix

# Solve and print
if model.solve():
    solution = {'sequence': sequence.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
