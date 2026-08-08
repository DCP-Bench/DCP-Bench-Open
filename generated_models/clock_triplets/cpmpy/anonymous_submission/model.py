from cpmpy import *
import json

# Decision Variables
x = intvar(1, 12, shape=12, name="x")  # Clock arrangement (x[0] is 12 o'clock position)

# Model
model = Model()

# Constraint: All numbers must be distinct (1-12)
model += AllDifferent(x)

# Constraint: First number must be 12 (12 o'clock position)
model += x[0] == 12

# Constraint: No triplet of adjacent numbers sums to more than 21
for i in range(12):
    # Handle circular arrangement (wrap around)
    triplet = [x[i], x[(i+1)%12], x[(i+2)%12]]
    model += sum(triplet) <= 21

# Constraint: At least one triplet sums to exactly 21
model += sum([sum([x[i], x[(i+1)%12], x[(i+2)%12]]) == 21 for i in range(12)]) >= 1

# Solve
model.solve()

# Print solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script