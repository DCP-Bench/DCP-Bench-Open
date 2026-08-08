
import cpmpy as cp
import json

# Data
n_steps = 20
allowed_moves = [0, 3, 4, 5]  # 0 allowed only after reaching the top
# End of data

# Model definition
model = cp.Model()

# Decision Variables
steps = cp.intvar(0, 5, shape=n_steps, name="steps")

# Constraints

# Each move must be either 0 (after finishing) or 3, 4, or 5
model += [cp.InDomain(steps[i], allowed_moves) for i in range(n_steps)]

# Total steps must exactly reach the top
model += (cp.sum(steps) == n_steps)

# Cumulative sum can never exceed the total number of steps
model += [cp.sum(steps[:k+1]) <= n_steps for k in range(n_steps)]

# No zeros until we have reached the top; once at the top, only zeros follow
model += [(steps[k] == 0).implies(cp.sum(steps[:k]) == n_steps) for k in range(n_steps)]

# Solve and print
if model.solve():
    solution = {'steps': steps.value().tolist()}
    # Ensure integers in list (CPMpy may already return ints, but enforce for safety)
    solution['steps'] = [int(v) for v in solution['steps']]
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
