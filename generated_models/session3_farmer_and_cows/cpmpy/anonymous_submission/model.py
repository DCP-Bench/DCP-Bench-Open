# Import libraries
from cpmpy import *
import json

# Decision Variables
cow_assignments = intvar(0, 4, shape=25, name="cow_assignments")  # 0-4 represent the 5 sons

# Model
model = Model()

# Constraint: number of cows assigned to each son
# Son 0 gets 7 cows, son 1 gets 6, ..., son 4 gets 3
model += sum(cow_assignments == 0) == 7
model += sum(cow_assignments == 1) == 6
model += sum(cow_assignments == 2) == 5
model += sum(cow_assignments == 3) == 4
model += sum(cow_assignments == 4) == 3

# Constraint: total milk production per son must be equal (65 kg each)
target_milk = 65
for son in range(5):
    model += sum((i+1) * (cow_assignments[i] == son) for i in range(25)) == target_milk

# Solve
model.solve()

# Print solution
solution = {
    "cow_assignments": cow_assignments.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script