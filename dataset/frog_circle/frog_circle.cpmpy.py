#!/usr/bin/python3
# Category: hakan_examples
# Source: https://www.hakank.org/cpmpy/frog_circle.py
# Source Description: https://www.cantorsparadise.com/flex-your-problem-solving-skills-with-this-viral-math-puzzle-cad27f6bffef
# Misc: https://artofproblemsolving.com/community/c2499895_2021_panamerican_girls_mathematical_olympiad

# Data
n = 12
# End of data

# Import libraries
from cpmpy import *
import numpy as np
import json

# declare variables
x = intvar(1, n, shape=(n,), name="x")
pos = intvar(0, n - 1, shape=(n,), name="pos")
visited = intvar(1, n, shape=(n,), name="visited")

# constraints
model = Model([AllDifferent(x),
               AllDifferent(pos),
               AllDifferent(visited),
               x[0] == 1,  # The frog starts on card 1 at position 0
               pos[0] == 0,
               visited[0] == 1,
               ])

# Loop through all the steps (except the initial)
for i in range(1, n):
    # The next position is the previous position + the value of x in that position
    model += [pos[i] == (pos[i - 1] + x[pos[i - 1]]) % n]
    # The number that is visited in this step
    model += [visited[i] == x[pos[i]]]

# The position for n is n at "6 o'clock"
# <SYMMETRY_BREAKING_CONSTRAINT_START>
# model += [pos[n - 1] == n // 2]
# model += [x[n // 2] == n]
# <SYMMETRY_BREAKING_CONSTRAINT_END>

# Solve
model.solve()

# Output
solution = {
    "x": x.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script