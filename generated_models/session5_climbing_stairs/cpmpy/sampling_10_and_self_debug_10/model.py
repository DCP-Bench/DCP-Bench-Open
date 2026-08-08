
import cpmpy as cp
import json

n = 20
m1 = 3
m2 = 5

model = cp.Model()

# Decision variables: steps taken at each move (length n)
# Each move can be 0 (no step) or between m1 and m2 inclusive
steps = cp.intvar(0, m2, shape=n, name="steps")

# Constraints:
# 1) The sum of all steps must be exactly n
model += (cp.sum(steps) == n)

# 2) Each step is either 0 or between m1 and m2 inclusive
# We enforce that if steps[i] != 0 then steps[i] >= m1
for i in range(n):
    # steps[i] == 0 or steps[i] >= m1
    model += ( (steps[i] == 0) | (steps[i] >= m1) )
    # steps[i] <= m2 already ensured by domain

# 3) After the last non-zero step, all subsequent steps must be zero
# Find the last non-zero step index and ensure all after are zero
# We can do this by enforcing that steps are zero after the last non-zero step
# We use a boolean array to indicate if step i is used
used = cp.boolvar(shape=n)
for i in range(n):
    model += (used[i] == (steps[i] != 0))

# The last used index is the max i where used[i] == True
# We enforce that for all i > last_used_index, steps[i] == 0
# We can do this by:
# For all i in [0..n-2], used[i+1] <= used[i] + (steps[i+1] == 0)
# But simpler is to enforce that used is non-increasing after last True
# Or we can enforce that used is prefix of ones then zeros:
# used is non-increasing: used[i] >= used[i+1]
for i in range(n-1):
    model += (used[i] >= used[i+1])

if model.solve():
    solution = {'steps': steps.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
