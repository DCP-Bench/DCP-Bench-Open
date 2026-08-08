import cpmpy as cp
import json

# Five Floors Problem: Assign Baker, Cooper, Fletcher, Miller, and Smith to floors 1-5
# with the given constraints

# Decision variables: floor number for each person (1-5)
B = cp.intvar(1, 5, name="Baker")     # Baker's floor
C = cp.intvar(1, 5, name="Cooper")    # Cooper's floor  
F = cp.intvar(1, 5, name="Fletcher")  # Fletcher's floor
M = cp.intvar(1, 5, name="Miller")    # Miller's floor
S = cp.intvar(1, 5, name="Smith")     # Smith's floor

model = cp.Model()

# Add all constraints
# 1. Baker does not live on the fifth floor
model += B != 5

# 2. Cooper does not live on the first floor  
model += C != 1

# 3. Fletcher does not live on either the fifth or the first floor
model += F != 1
model += F != 5

# 4. Miller lives on a higher floor than Cooper
model += M > C

# 5. Smith does not live on a floor adjacent to Fletcher's
model += cp.abs(S - F) != 1

# 6. Fletcher does not live on a floor adjacent to Cooper's
model += cp.abs(F - C) != 1

# 7. They all live on different floors
model += cp.AllDifferent([B, C, F, M, S])

# Solve the model
if model.solve():
    # Create solution in required JSON format
    solution = {
        "B": B.value(),
        "C": C.value(),
        "F": F.value(),
        "M": M.value(),
        "S": S.value()
    }
    
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))