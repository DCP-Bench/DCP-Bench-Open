import cpmpy as cp
import json

# Problem: Find 4-digit PIN abcd where:
# 1. No two digits are the same
# 2. cd = 3 * ab (2-digit numbers)
# 3. da = 2 * bc (2-digit numbers)

# Decision variables: 4 digits of the PIN
a = cp.intvar(1, 9, name="a")  # First digit cannot be 0 for a valid PIN
b = cp.intvar(0, 9, name="b")
c = cp.intvar(0, 9, name="c") 
d = cp.intvar(0, 9, name="d")

model = cp.Model()

# Constraint 1: All digits are different
model += cp.AllDifferent([a, b, c, d])

# Constraint 2: cd = 3 * ab
# 10*c + d = 3 * (10*a + b)
model += (10*c + d) == 3 * (10*a + b)

# Constraint 3: da = 2 * bc  
# 10*d + a = 2 * (10*b + c)
model += (10*d + a) == 2 * (10*b + c)

# Solve the model
if model.solve():
    # Extract solution in required JSON format
    solution = {
        "a": int(a.value()),
        "b": int(b.value()), 
        "c": int(c.value()),
        "d": int(d.value())
    }
    
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))