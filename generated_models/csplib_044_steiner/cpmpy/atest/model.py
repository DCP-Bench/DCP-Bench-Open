from cpmpy import *
import json

# Parameters
n = 9  # Order of the Steiner Triple System
num_triples = n * (n - 1) // 6  # Number of triples to find

# Decision variables
# We will represent the set of triples as a list of 3-element sets
# To model this, we use integer variables for each element in the triples
# We will use a 2D array of size (num_triples, 3) to represent the triples
triples = intvar(1, n, shape=(num_triples, 3), name="triples")

# Model
model = Model()

# Each triple must contain distinct elements
for i in range(num_triples):
    model += [AllDifferent(triples[i])]

# Each element from 1 to n must appear in exactly (n - 1) // 2 triples
for element in range(1, n + 1):
    model += [sum((triples == element).sum(axis=1)) == (n - 1) // 2]

# Any two triples must share at most one element
for i in range(num_triples):
    for j in range(i + 1, num_triples):
        # Count the number of common elements between triples[i] and triples[j]
        common_elements = sum([triples[i, k] == triples[j, l] for k in range(3) for l in range(3)])
        model += [common_elements <= 1]

# Solve the model
model.solve()

# Convert the solution to a list of lists (JSON serializable)
solution_triples = [triples[i].value().tolist() for i in range(num_triples)]

# Output the solution
solution = {"sets": solution_triples}
print(json.dumps(solution))