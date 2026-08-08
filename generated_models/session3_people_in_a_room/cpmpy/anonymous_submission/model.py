# Import libraries
from cpmpy import *
import json

# Parameters
total_people = 13
num_males = 4
num_females = total_people - num_males

# Decision Variables
sequence = intvar(0, 1, shape=total_people, name="sequence")  # 0=male, 1=female

# Model
model = Model()

# Exactly 4 males and 9 females
model += sum(sequence == 0) == num_males
model += sum(sequence == 1) == num_females

# Ratio constraint at every step
for step in range(1, total_people+1):
    current_males = sum(sequence[:step] == 0)
    current_females = sum(sequence[:step] == 1)
    # Females/males <= 7/3 => 3*females <= 7*males
    model += (3 * current_females <= 7 * current_males)

# Solve
model.solve()

# Print solution
solution = {
    "sequence": [bool(x) for x in sequence.value().tolist()]
}
print(json.dumps(solution))
# End of CPMPy script