#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob007_all_interval.py
# Source description: https://www.csplib.org/Problems/prob007/

# Data
n = 12  # Number of pitch-classes
# End of data

# Import libraries
from cpmpy import *
import numpy as np
import json

# Create the solver
model = Model()

# Declare variables
x = intvar(0, n - 1, shape=n, name="x")  # Pitch-classes
diffs = intvar(1, n - 1, shape=n - 1, name="diffs")  # Intervals

# Constraints
model += [AllDifferent(x),
          AllDifferent(diffs)]

# Differences between successive values
model += diffs == np.abs(x[1:] - x[:-1])

# Symmetry breaking
# <SYMMETRY_BREAKING_CONSTRAINT_START>
# model += [x[0] < x[-1]]  # Mirroring array is equivalent solution
# model += [diffs[0] < diffs[1]]  # Further symmetry breaking
# <SYMMETRY_BREAKING_CONSTRAINT_END>

# Solve
model.solve()

# Print
solution = {"x": x.value().tolist(), "diffs": diffs.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
