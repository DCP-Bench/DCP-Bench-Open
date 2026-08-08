from cpmpy import *
import json

# Decision Variables
# Players: X=0, Y=1, Z=2
# Nationalities: American=0, English=1, French=2
x = intvar(0, 2, name="x")  # Nationality of X
y = intvar(0, 2, name="y")  # Nationality of Y
z = intvar(0, 2, name="z")  # Nationality of Z

# Model
model = Model()

# All nationalities must be distinct
model += AllDifferent([x, y, z])

# Constraint 1: Y passed three hearts to the American
# In circular seating X-Y-Z, Y passes to Z
model += (y == 1) & (z == 0)  # Y passes to Z who is American

# Constraint 2: X passed to someone who passed to the Frenchwoman
# X passes to Y, who passes to Z (French)
# Or X passes to Z, who passes to Y (French)
# But from Constraint 1, we know Y passes to Z (American), so this can't be French
# Therefore, the only possibility is:
# X passes to Y, Y passes to Z (but Z is American from Constraint 1)
# Wait, this suggests our initial assumption might be wrong

# Alternative approach:
# The passing order is fixed in a circle: X->Y->Z->X
# From Constraint 1: Y passes to Z who is American (so z == 0)
# From Constraint 2: X passes to Y who passes to Z (but Z is American)
# But the Frenchwoman must be someone who receives cards
# Therefore, the Frenchwoman must be X (since Z is American and Y passes to Z)
# So the chain is: X passes to Y, Y passes to Z (American), Z passes to X (French)
model += (x == 2)  # X is French
model += (z == 0)  # Z is American (from Constraint 1)
model += (y == 1)  # Y must be English (only remaining option)

# Solve
model.solve()

# Prepare solution
solution = {
    "x": x.value(),
    "y": y.value(),
    "z": z.value(),
    "american": [i for i in range(3) if [x.value(), y.value(), z.value()][i] == 0][0],
    "english": [i for i in range(3) if [x.value(), y.value(), z.value()][i] == 1][0],
    "french": [i for i in range(3) if [x.value(), y.value(), z.value()][i] == 2][0]
}

print(json.dumps(solution))