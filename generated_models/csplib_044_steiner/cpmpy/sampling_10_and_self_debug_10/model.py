
import cpmpy as cp
import json
import numpy as np

# Data
n = 9
# Number of triples
num_triples = n * (n - 1) // 6

# Model definition
model = cp.Model()

# Decision Variables
# triples[i, j]: the j-th element of the i-th triple (1-based elements)
triples = cp.intvar(1, n, shape=(num_triples, 3), name="triples")

# Constraints

# 1) Each triple has distinct elements
for i in range(num_triples):
    model += cp.AllDifferent(triples[i])

# 2) Sort each triple to avoid permutations of the same triple
# Enforce triples[i,0] < triples[i,1] < triples[i,2]
for i in range(num_triples):
    model += triples[i, 0] < triples[i, 1]
    model += triples[i, 1] < triples[i, 2]

# 3) Any two triples have at most one common element
# For each pair of triples, count common elements <= 1
for i in range(num_triples):
    for j in range(i + 1, num_triples):
        # Count common elements between triples[i] and triples[j]
        # We create boolean variables for each pair of elements equalities
        common = []
        for a in range(3):
            for b in range(3):
                common.append(triples[i, a] == triples[j, b])
        model += cp.sum(common) <= 1

# 4) Each element appears exactly (n-1)/2 times in the triples
# Count occurrences of each element in all triples
occurrences = []
for elem in range(1, n + 1):
    occ = cp.Count(triples, elem)
    occurrences.append(occ)
    model += occ == (n - 1) // 2

# Solve and print
if model.solve():
    # Extract triples as sorted lists
    solution_triples = triples.value().tolist()
    # Convert each triple to a set (list) of integers
    # Already sorted and distinct by constraints
    solution = {'sets': solution_triples}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
