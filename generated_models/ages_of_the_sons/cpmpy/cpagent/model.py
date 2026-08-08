import cpmpy as cp
import json

# Problem: Find ages of three sons where:
# 1. Product of ages = 36
# 2. Sum of ages creates ambiguity (must be 13, the only sum appearing twice)
# 3. There is a unique oldest son (breaks the ambiguity)

# Decision variables: ages of the three sons (A1=oldest, A2=middle, A3=youngest)
A1 = cp.intvar(1, 36, name="A1")  # Oldest son
A2 = cp.intvar(1, 36, name="A2")  # Middle son  
A3 = cp.intvar(1, 36, name="A3")  # Youngest son

model = cp.Model()

# Constraint 1: Product of ages is 36
model += A1 * A2 * A3 == 36

# Constraint 2: Sum equals 13 (the ambiguous sum from the puzzle logic)
model += A1 + A2 + A3 == 13

# Constraint 3: A1 is uniquely the oldest (breaks ambiguity)
model += A1 > A2
model += A1 > A3

# Constraint 4: Order remaining ages for canonical solution
model += A2 >= A3

# Solve the model
if model.solve():
    solution = {
        "A1": int(A1.value()),
        "A2": int(A2.value()),
        "A3": int(A3.value())
    }
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))