
import cpmpy as cp
import json

# The product of the ages is 36
product = 36

# Model definition
model = cp.Model()

# Decision Variables: ages of the three sons, positive integers
# Since product is 36, max age can be at most 36
A = cp.intvar(1, 36, shape=3, name="A")

# Constraints
# 1) Product of ages is 36
model += (A[0] * A[1] * A[2] == product)

# 2) The sum of ages equals the number of windows in the building
# The mathematician still needs more info after knowing the sum,
# so the sum must not uniquely identify the ages.
# So we will find all triplets with product=36 and group by sum,
# then only sums with multiple triplets remain possible.
# We will add this logic after solving.

# 3) The oldest son has blue eyes
# This implies there is a unique oldest son (strictly oldest)
# So the maximum age must be unique (not tied)
# So max age is strictly greater than the other two ages
model += (A[0] >= A[1])
model += (A[1] >= A[2])
model += (A[0] > A[1])  # oldest is strictly older than second oldest

# We want to find all solutions satisfying product=36 and sorted descending ages with unique oldest

# Solve all solutions
solutions = []
while model.solve():
    sol = A.value().tolist()
    solutions.append(sol)
    # Add constraint to exclude this solution for next search
    model += (cp.sum([ (A[i] != sol[i]) for i in range(3)]) > 0)

# Now, from all solutions, find sums that appear more than once (ambiguous sums)
from collections import defaultdict
sum_to_solutions = defaultdict(list)
for sol in solutions:
    s = sum(sol)
    sum_to_solutions[s].append(sol)

# The mathematician needed more info after sum, so sum must be ambiguous (multiple solutions)
ambiguous_sums = {s: sols for s, sols in sum_to_solutions.items() if len(sols) > 1}

# The last clue "oldest son has blue eyes" means unique oldest son, which we already enforced.
# So the final solution is the unique solution among ambiguous sums with unique oldest.

# From ambiguous sums, pick the one with unique oldest son (already filtered)
# There should be exactly one such solution.

# The classic known solution is (9,2,2) with sum=13, product=36, unique oldest son 9
# Let's confirm this is in ambiguous sums

final_solution = None
for s, sols in ambiguous_sums.items():
    # Among sols, all have unique oldest son by construction
    # If only one solution in sols, that is the answer
    # But ambiguous sums have multiple solutions, so pick the one with unique oldest son
    # We already enforced unique oldest son in model, so all sols have unique oldest son
    # So the ambiguous sums here are sums with multiple solutions with unique oldest son
    # But this contradicts the puzzle logic, so we relax unique oldest son constraint for now and do manual filtering

    # Actually, the puzzle logic is:
    # - product=36
    # - sum = number of windows (ambiguous sum)
    # - oldest son has blue eyes => unique oldest son (max age strictly greater than others)
    # So we must find sums with multiple triplets (ambiguous sums)
    # Then among those triplets, only one has unique oldest son

    # So let's redo the search without unique oldest son constraint, then filter manually

    pass

# Redo search without unique oldest son constraint
model = cp.Model()
A = cp.intvar(1, 36, shape=3, name="A")
model += (A[0] * A[1] * A[2] == product)
model += (A[0] >= A[1])
model += (A[1] >= A[2])

solutions = []
while model.solve():
    sol = A.value().tolist()
    solutions.append(sol)
    model += (cp.sum([ (A[i] != sol[i]) for i in range(3)]) > 0)

sum_to_solutions = defaultdict(list)
for sol in solutions:
    s = sum(sol)
    sum_to_solutions[s].append(sol)

# Find ambiguous sums (multiple solutions)
ambiguous_sums = {s: sols for s, sols in sum_to_solutions.items() if len(sols) > 1}

# Now, for each ambiguous sum, check which solution has unique oldest son
# The oldest son is unique if max age > second max age
def unique_oldest(sol):
    return sol[0] > sol[1]

final_solution = None
for s, sols in ambiguous_sums.items():
    sols_with_unique_oldest = [sol for sol in sols if unique_oldest(sol)]
    if len(sols_with_unique_oldest) == 1:
        final_solution = sols_with_unique_oldest[0]
        break

# Print the solution starting from oldest
if final_solution:
    solution = {'A1': int(final_solution[0]), 'A2': int(final_solution[1]), 'A3': int(final_solution[2])}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
