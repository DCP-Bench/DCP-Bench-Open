
import cpmpy as cp
import json

# Weights of all pairs given
pair_weights = [80, 82, 83, 84, 85, 86, 87, 88, 90, 91]

# Model definition
model = cp.Model()

# Decision Variables: weights of the 5 bales
bales = cp.intvar(1, 100, shape=5, name="bales")

# Sort the bales weights for symmetry breaking (optional but helps)
model += bales[0] <= bales[1]
model += bales[1] <= bales[2]
model += bales[2] <= bales[3]
model += bales[3] <= bales[4]

# Compute all pairs sums
pair_sums = []
for i in range(5):
    for j in range(i+1, 5):
        pair_sums.append(bales[i] + bales[j])

# The pair sums must be exactly the given sorted list
# We enforce that the sorted list of pair_sums equals pair_weights
# CPMpy does not have built-in sorting constraints, so we create auxiliary variables
# Create sorted_pair_sums variables
sorted_pair_sums = cp.intvar(min(pair_weights), max(pair_weights), shape=10, name="sorted_pair_sums")

# sorted_pair_sums is sorted non-decreasing
for k in range(9):
    model += sorted_pair_sums[k] <= sorted_pair_sums[k+1]

# sorted_pair_sums is a permutation of pair_sums
# We use global cardinality to enforce that each value in pair_weights appears the same number of times in pair_sums and sorted_pair_sums
# Since the pair_weights list has unique values, we enforce that sorted_pair_sums matches pair_weights
for v, w in enumerate(pair_weights):
    # Number of occurrences of w in sorted_pair_sums == 1
    model += cp.Count(sorted_pair_sums, w) == 1

# sorted_pair_sums is a permutation of pair_sums
# The pair_sums and sorted_pair_sums arrays are permutations => both multisets are equal
# We use global cardinality count for pair_sums to have same count as sorted_pair_sums
# Since values are distinct, we enforce that the multiset of pair_sums matches sorted_pair_sums by posting the channeling constraints
model += cp.AllDifferent(pair_sums)  # The sums must be distinct because the pair_weights are distinct
model += cp.AllDifferent(sorted_pair_sums)  # Already distinct by pair_weights

# Channeling: sorted_pair_sums is a permutation of pair_sums
# We post that for all values in pair_weights, pair_sums contain these values
for val in pair_weights:
    model += cp.Count(pair_sums, val) == 1

# Additional constraint to reduce symmetry:
# The smallest pair sum must be bales[0] + bales[1]
model += bales[0] + bales[1] == pair_weights[0]

# The largest pair sum must be bales[3] + bales[4]
model += bales[3] + bales[4] == pair_weights[-1]

# Solve and print
if model.solve():
    solution = {'bales': bales.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
