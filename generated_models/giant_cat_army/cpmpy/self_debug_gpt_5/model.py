
import cpmpy as cp
import json

# Data (construct allowed transitions)
# Allowed transitions: (a -> a+5), (a -> a+7), and (sq -> sqrt(sq)) for sq in {0,1,4,9,16,25,36,49}
allowed_pairs = []
for a in range(0, 61):
    if a + 5 <= 60:
        allowed_pairs.append([a, a + 5])
    if a + 7 <= 60:
        allowed_pairs.append([a, a + 7])
# sqrt transitions
for i in range(0, 8):  # 0..7, squares up to 49
    sq = i * i
    if sq <= 60:
        allowed_pairs.append([sq, i])

# Model definition
model = cp.Model()

# Decision Variables
x = cp.intvar(0, 60, shape=24, name="x")

# Constraints
model += (x[0] == 0)
model += (x[-1] == 14)
model += cp.AllDifferent(x)

# Transition constraints via Table of allowed pairs
for i in range(1, 24):
    model += cp.Table([x[i-1], x[i]], allowed_pairs)

# Ensure 2 and 10 appear exactly once; 14 is already fixed at the end
model += (cp.Count(x, 2) == 1)
model += (cp.Count(x, 10) == 1)
model += (cp.Count(x, 14) == 1)

# Enforce order: 2 appears before 10, which appears before 14
model += cp.Precedence(x, [2, 10, 14])

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
