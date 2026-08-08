import cpmpy as cp
import json

# Problem: Find 4 different numbers a, b, c, d in {1, 2, ..., 100} 
# such that a^2 + b^2 = c^2 + d^2

# Decision variables: a, b, c, d are integers between 1 and 100
a = cp.intvar(1, 100, name="a")
b = cp.intvar(1, 100, name="b") 
c = cp.intvar(1, 100, name="c")
d = cp.intvar(1, 100, name="d")

# Create the model
model = cp.Model()

# Constraint 1: All four numbers must be different
model += cp.AllDifferent([a, b, c, d])

# Constraint 2: Mathematical constraint a^2 + b^2 = c^2 + d^2
model += a*a + b*b == c*c + d*d

# Performance improvement: Add symmetry breaking
# Order a < b and c < d to reduce search space
model += a < b
model += c < d

# Order the pairs: ensure (a,b) comes before (c,d) lexicographically
model += (a < c) | ((a == c) & (b < d))

# Solve the model (satisfaction problem)
if model.solve():
    # Extract solution values
    solution = {
        "a": a.value(),
        "b": b.value(),
        "c": c.value(),
        "d": d.value()
    }
    
    # Output the solution in the required JSON format
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))