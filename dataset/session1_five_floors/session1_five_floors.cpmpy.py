#!/usr/bin/python3
# Category: aplai_course
# Source: http://www.hakank.org/cpmpy/five_floors.py

"""
Baker, Cooper, Fletcher, Miller, and Smith live on the first five floors of an apartment house. Baker does not
live on the fifth floor. Cooper does not live on the first floor. Fletcher does not live on either the fifth or the
first floor. Miller lives on a higher floor than does Cooper. Smith does not live on a floor adjacent to Fletcher’.
Fletcher does not live on a floor adjacent to Cooper’s. They all live on different floors. Find the floors where
these people live.

Print the floors where each person lives (B, C, F, M, S).
"""

# Import libraries
from cpmpy import *
import json

# Decision Variables
B = intvar(1, 5)  # Baker
C = intvar(1, 5)  # Cooper
F = intvar(1, 5)  # Fletcher
M = intvar(1, 5)  # Miller
S = intvar(1, 5)  # Smith

# Constraints
model = Model()

model += B != 5  # Baker does not live on the fifth floor
model += C != 1  # Cooper does not live on the first floor
model += (F != 5) & (F != 1)  # Fletcher does not live on either the fifth or the first floor
model += M > C  # Miller lives on a higher floor than does Cooper
model += abs(S - F) != 1  # Smith does not live on a floor adjacent to Fletcher
model += abs(F - C) != 1  # Fletcher does not live on a floor adjacent to Cooper
model += AllDifferent([B, C, F, M, S])  # They all live on different floors

# Solve
model.solve()

# Print the solution
solution = {"B": B.value(), "C": C.value(), "F": F.value(), "M": M.value(), "S": S.value()}
print(json.dumps(solution))
# End of CPMPy script
