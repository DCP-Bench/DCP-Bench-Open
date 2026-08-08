# Import libraries
from cpmpy import *
import json

# Parameters
size = 10  # Number of marks on the Golomb ruler

# Decision variables
marks = intvar(0, 1000, shape=size, name="marks")  # Upper bound 1000 is arbitrary

# Ensure marks are strictly increasing
model = Model([
    [marks[i] < marks[i + 1] for i in range(size - 1)]
])

# Collect all pairwise differences into a single array
differences = []
for i in range(size):
    for j in range(i + 1, size):
        differences.append(marks[j] - marks[i])

# Convert the list of expressions to a CPMpy array
differences_array = cpm_array(differences)

# Ensure all differences are distinct
model += AllDifferent(differences_array)

# Symmetry breaking constraint: first difference < last difference
model += (marks[1] - marks[0] < marks[-1] - marks[-2])

# Solve the model
model.solve()

# Prepare the solution
solution = {
    "marks": marks.value().tolist(),
    "length": marks[-1].value()
}

# Print the solution
print(json.dumps(solution))