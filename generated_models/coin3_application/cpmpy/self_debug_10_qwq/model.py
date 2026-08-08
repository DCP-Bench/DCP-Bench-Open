
import cpmpy as cp
import json

coins = [1, 2, 5, 10, 20, 50]

# Decision variables: counts for each coin denomination
x = cp.intvar(0, 100, shape=len(coins), name="x")

model = cp.Model()

# For each amount from 1 to 99, ensure there exists a combination of coins that sums to it
for a in range(1, 100):
    # Variables for the counts used in this amount's combination
    c = cp.intvar(0, 100, shape=len(coins), name=f"c_{a}")
    
    # Constraint: combination must sum to the current amount
    model += (cp.sum(coins[i] * c[i] for i in range(6)) == a)
    
    # Constraints: combination counts cannot exceed the available coin counts
    for i in range(6):
        model += (c[i] <= x[i])

# Objective: minimize the total number of coins
model.minimize(cp.sum(x))

if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
