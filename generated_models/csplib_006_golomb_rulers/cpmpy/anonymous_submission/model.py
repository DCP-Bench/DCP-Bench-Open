# Import libraries
from cpmpy import *
import json

# Parameters
size = 10  # Number of marks on the Golomb ruler

# Decision Variables
marks = intvar(0, 1000, shape=size, name="marks")  # Positions of marks
length = intvar(0, 1000, name="length")  # Total length of the Golomb ruler

# Model
model = Model()

# Constraint: marks must be in increasing order
model += [marks[i] < marks[i+1] for i in range(size-1)]

# Constraint: first mark is 0
model += marks[0] == 0

# Constraint: length is the last mark
model += length == marks[-1]

# Constraint: all differences between marks must be distinct
differences = []
for i in range(size):
    for j in range(i+1, size):
        differences.append(marks[j] - marks[i])
model += AllDifferent(differences)

# Symmetry breaking: first difference is less than last difference
model += (marks[1] - marks[0]) < (marks[-1] - marks[-2])

# Objective: minimize the length
model.minimize(length)

# Solve
model.solve()

# Print solution
solution = {
    "marks": marks.value().tolist(),
    "length": length.value()
}
print(json.dumps(solution))
# End of CPMPy script