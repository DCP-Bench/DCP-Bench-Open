import cpmpy as cp
import json

# Abbot's Puzzle: Distribute 100 bushels among 100 people
# Constraints:
# 1. men + women + children = 100 (total people)
# 2. 3*men + 2*women + 0.5*children = 100 (total bushels)
# 3. women = 5*men (five times as many women as men)

model = cp.Model()

# Decision variables
men = cp.intvar(0, 100, name="men")
women = cp.intvar(0, 100, name="women") 
children = cp.intvar(0, 100, name="children")

# Constraints
# Total people = 100
model += men + women + children == 100

# Total bushels = 100 (scaled by 2 to avoid floats: 6*men + 4*women + children = 200)
model += 6*men + 4*women + children == 200

# Five times as many women as men
model += women == 5*men

# Solve
if model.solve():
    solution = {
        "men": int(men.value()),
        "women": int(women.value()),
        "children": int(children.value())
    }
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))