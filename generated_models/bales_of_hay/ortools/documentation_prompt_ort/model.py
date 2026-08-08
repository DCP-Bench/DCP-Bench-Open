from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Decision Variables: weights of the 5 bales
# Assuming weights are positive and reasonable upper bound (e.g., 100)
bales = [model.NewIntVar(1, 100, f'bale_{i}') for i in range(5)]

# We know the pair sums sorted:
pair_sums_sorted = [80, 82, 83, 84, 85, 86, 87, 88, 90, 91]

# Generate all pairs (i < j)
pairs = []
for i in range(5):
    for j in range(i + 1, 5):
        pairs.append((i, j))

# There are 10 pairs, create variables for their sums
pair_sums = [model.NewIntVar(2, 200, f'pair_sum_{i}') for i in range(10)]

# Link pair sums to bales weights
for idx, (i, j) in enumerate(pairs):
    model.Add(pair_sums[idx] == bales[i] + bales[j])

# The pair sums must be exactly the given sorted list, but we don't know which pair corresponds to which sum.
# So the multiset of pair_sums must be equal to the given pair_sums_sorted.
# We enforce that the pair_sums variables are a permutation of the given sorted sums.
# To do this, we use the AllDifferent constraint on pair_sums and enforce that their sorted values equal pair_sums_sorted.
# But pair sums can have duplicates, so AllDifferent is not applicable.
# Instead, we enforce that the multiset of pair_sums equals the multiset of pair_sums_sorted.
# We can do this by enforcing that the count of each value in pair_sums equals the count in pair_sums_sorted.
# Since all values are distinct in pair_sums_sorted, we can enforce that pair_sums is a permutation of pair_sums_sorted.

# Create boolean variables for assignment of pair_sums to pair_sums_sorted values
assignments = []
for i in range(10):
    row = []
    for val in pair_sums_sorted:
        b = model.NewBoolVar(f'assignment_{i}_{val}')
        row.append(b)
    assignments.append(row)

# Each pair_sum must be assigned exactly one value from pair_sums_sorted
for i in range(10):
    model.AddExactlyOne(assignments[i])

# Each value in pair_sums_sorted must be assigned exactly once
for j in range(10):
    model.AddExactlyOne(assignments[i][j] for i in range(10))

# Link assignments to pair_sums values
for i in range(10):
    # pair_sums[i] == sum of val * assignments[i][val_index]
    # Since only one assignment[i][val_index] is true, pair_sums[i] == that val
    model.Add(sum(assignments[i][j] * pair_sums_sorted[j] for j in range(10)) == pair_sums[i])

# Add ordering constraints to break symmetry in bales weights (optional but helps solver)
for i in range(4):
    model.Add(bales[i] <= bales[i + 1])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'bales': [solver.Value(b) for b in bales]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")