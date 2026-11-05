#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob006_golomb.py
# Source description: https://www.csplib.org/Problems/prob006/

# Data
size = 10  # Number of marks on the Golomb ruler
# End of data

# Import libraries
from cpmpy import *
import json

# Decision variables
marks = intvar(0, size * size, shape=size, name="marks")
length = marks[-1]

# Model
model = Model()

# first mark is 0
model += (marks[0] == 0)

# marks must be increasing
model += marks[:-1] < marks[1:]

# golomb constraint
diffs = [marks[j] - marks[i] for i in range(0, size - 1) for j in range(i + 1, size)]
model += AllDifferent(diffs)

# Symmetry breaking
# <SYMMETRY_BREAKING_CONSTRAINT_START>
# model += (marks[size - 1] - marks[size - 2] > marks[1] - marks[0])
# model += (diffs[0] < diffs[size - 1])
# <SYMMETRY_BREAKING_CONSTRAINT_END>

# find optimal ruler
model.minimize(length)

# Solve
model.solve()

# Print
solution = {"marks": marks.value().tolist(), "length": length.value()}
print(json.dumps(solution))
# End of CPMPy script
