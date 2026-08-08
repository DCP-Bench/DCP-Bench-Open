
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
sol = cp.intvar(1, 4, shape=8, name="sol")
starts = [cp.intvar(0, 7 - (k + 1), name=f"s_{k}") for k in range(1, 5)]  # start positions for each k

# Constraints
for idx, k in enumerate(range(1, 5)):
    s_k = starts[idx]
    # Place the two k's at positions s_k and s_k + k + 1
    model += (sol[s_k] == k)
    model += (sol[s_k + k + 1] == k)
    # Exactly two occurrences of k
    model += (cp.Count(sol, k) == 2)

# Solve and print
if model.solve():
    solution = {'sol': sol.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
