#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/averbach_1_2.py

"""Three players (X, Y, Z) of different nationalities (American, English, French) are seated around a circular
table playing a game of Hearts. Each passed three cards to the person on their right. Y passed three hearts to the
American, X passed the queen of spades and two diamonds to the person who passed their cards to the Frenchwoman.
Determine the nationality of each person.

Print the values of X, Y, Z, American, English, French (x, y, z, american, english, french), such that the
same value denotes the matching between the person and their nationality. Use 0, 1 or 2.
"""

# Import libraries
from cpmpy import *
import json


# a is right to b
def right_to(a, b):
    return a == (b + 1) % 3


n = 3

# variables
players = intvar(0, 2, shape=n, name="players")
x, y, z = players

nationalities = intvar(0, 2, shape=n, name="women")
american, english, french = nationalities

model = Model([AllDifferent(players),
               AllDifferent([american, english, french]),
               right_to(american, y),
               right_to(x, french),

               # symmetry breaking
               # <SYMMETRY_BREAKING_CONSTRAINT_START>
               # x == 0
               # <SYMMETRY_BREAKING_CONSTRAINT_END>
               ])

model.solve()

# Print the solution
solution = {"x": x.value(), "y": y.value(), "z": z.value(), "american": american.value(), "english": english.value(),
            "french": french.value()}
print(json.dumps(solution))
# End of CPMPy script
