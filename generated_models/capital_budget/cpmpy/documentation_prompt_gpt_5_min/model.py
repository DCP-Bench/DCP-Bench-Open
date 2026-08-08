
import cpmpy as cp
import json

# Data
costs = [5000, 7000, 4000, 3000]   # present outflows for investments 1-4
npvs  = [16000, 22000, 12000, 8000] # NPVs for investments 1-4
budget = 14000

# Model definition
model = cp.Model()

# Decision Variables: x[i] = 1 if investment i is chosen, 0 otherwise
x = cp.intvar(0, 1, shape=4, name="x")

# Constraints: total cost within available budget
model += cp.sum([costs[i] * x[i] for i in range(4)]) <= budget

# Objective: maximize total NPV (in dollars)
total_npv = cp.sum([npvs[i] * x[i] for i in range(4)])
model.maximize(total_npv)

# Solve and print
if model.solve():
    # z should be in thousands of dollars (e.g., 16 for $16,000)
    solution = {
        'x': x.value().tolist(),
        'z': int(model.objective_value()) // 1000
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
