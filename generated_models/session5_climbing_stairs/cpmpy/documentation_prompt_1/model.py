
import cpmpy as cp
import json

n = 20
m1 = 3
m2 = 5

model = cp.Model()

# Decision variables: steps taken at each move (up to n moves)
# Each move can be 0 (no step) or between m1 and m2 inclusive
steps = cp.intvar(0, m2, shape=n, name="steps")

# Constraints:
# 1) Each step is either 0 or between m1 and m2
for i in range(n):
    model += ( (steps[i] == 0) | ((steps[i] >= m1) & (steps[i] <= m2)) )

# 2) The sum of all steps must be exactly n
model += (cp.sum(steps) == n)

# 3) Once we reach the top (sum of steps so far == n), all subsequent steps must be 0
# We enforce that the prefix sums are <= n, and after sum == n, no more steps
prefix_sum = 0
for i in range(n):
    prefix_sum += steps[i]
    model += (prefix_sum <= n)
    # If prefix_sum == n at step i, then steps[j] == 0 for all j > i
    # We can enforce this by: if prefix_sum == n at i, then steps[i+1..n-1] == 0
    # Using implication constraints:
    if i < n-1:
        model += ( (prefix_sum == n).implies(cp.sum(steps[i+1:]) == 0) )

# Solve and print
if model.solve():
    solution = {'steps': steps.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
