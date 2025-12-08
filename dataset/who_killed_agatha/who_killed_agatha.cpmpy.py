#!/usr/bin/python3
# Category: cpmpy_examples
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/who_killed_agatha.py
# Source description: http://www.hakank.org/constraint_programming_blog/2014/11/decision_management_community_november_2014_challenge_who_killed_agath.html

"""
Someone in Dreadsbury Mansion killed Aunt Agatha.
Agatha, the butler, and Charles live in Dreadsbury Mansion, and
are the only ones to live there. A killer always hates, and is
no richer than his victim. Charles hates noone that Agatha hates.
Agatha hates everybody except the butler. The butler hates everyone
not richer than Aunt Agatha. The butler hates everyone whom Agatha hates.
Noone hates everyone. Who killed Agatha?

Print the 0-based index of the killer (killer).
"""

# Data
names = ["Agatha herself", "the butler", "Charles"]
# End of data

# Import libraries
from cpmpy import *
import json

# Agatha, the butler, and Charles live in Dreadsbury Mansion, and
# are the only ones to live there.
n = 3
(agatha, butler, charles) = range(n)  # enum constants

# Who killed agatha?
victim = agatha
killer = intvar(0, n - 1, name="killer")  # 0=Agatha, 1=butler, 2=Charles

hates = boolvar(shape=(n, n), name="hates")
richer = boolvar(shape=(n, n), name="richer")

model = Model(
    # A killer always hates, and is no richer than, his victim.
    # note; 'killer' is a variable, so must write ==1/==0 explicitly
    hates[killer, victim] == 1,
    richer[killer, victim] == 0,

    # implied richness: no one richer than himself, and anti-reflexive
    [~richer[i, i] for i in range(n)],
    [(richer[i, j]) == (~richer[j, i]) for i in range(n) for j in range(i + 1, n)],

    # Charles hates noone that Agatha hates.
    [(hates[agatha, i]).implies(~hates[charles, i]) for i in range(n)],

    # Agatha hates everybody except the butler.
    hates[agatha, (agatha, charles, butler)] == [1, 1, 0],

    # The butler hates everyone not richer than Aunt Agatha.
    [(~richer[i, agatha]).implies(hates[butler, i]) for i in range(n)],

    # The butler hates everyone whom Agatha hates.
    [(hates[agatha, i]).implies(hates[butler, i]) for i in range(n)],

    # Noone hates everyone.
    [sum(hates[i, :]) <= 2 for i in range(n)],
)

# Solve
model.solve()

# Print
solution = {"killer": killer.value()}
print(json.dumps(solution))
# End of CPMPy script
