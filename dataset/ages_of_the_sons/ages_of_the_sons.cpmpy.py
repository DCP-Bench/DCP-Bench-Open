#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/ages_of_the_sons.py
# Source description: http://blog.athico.com/2007/08/drools-puzzle-round-1-ages-of-sons.html

# Import libraries
from cpmpy import *
import json


A1 = intvar(0, 36, name="A1")  # oldest son
A2 = intvar(0, 36, name="A2")
A3 = intvar(0, 36, name="A3")

B1 = intvar(0, 36, name="B1")
B2 = intvar(0, 36, name="B2")
B3 = intvar(0, 36, name="B3")
AS = intvar(0, 1000, name="AS")
BS = intvar(0, 1000, name="BS")

model = Model([A1 > A2,
               A2 >= A3,
               36 == A1 * A2 * A3,

               B1 >= B2,
               B2 >= B3,
               A1 != B1,

               36 == B1 * B2 * B3,
               AS == A1 + A2 + A3,
               BS == B1 + B2 + B3,
               AS == BS
               ])

# Solve
model.solve()

# Print the solution
solution = {"A1": A1.value(), "A2": A2.value(), "A3": A3.value()}
print(json.dumps(solution))
# End of CPMPy script
