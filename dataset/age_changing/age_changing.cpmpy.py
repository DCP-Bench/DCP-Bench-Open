#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/age_changing.py
# Source description: https://enigmaticcode.wordpress.com/2015/06/20/enigma-1224-age-changing/

"""
If you start with my age, in years, and apply the four operations:

[
   +2  /8

   -3  *7

]

in some order, then the final answer you get is my husband's age.

Funnily enough, if you start with his age and apply the same four operations in a
different order, then you get my age.

What are our two ages?

Print my age and my husband's age (m, h).
"""

# Import libraries
from cpmpy import *
import json

def check(perm, old, new):
    return [
        (perm == 0).implies(new == old + 2),
        # (perm == 1).implies(new == old / 8), # This give a lot of bad solutions
        (perm == 1).implies(8*new == old),     # This works
        (perm == 2).implies(new == old - 3),
        (perm == 3).implies(new == old * 7)
        ]

n = 4

perms = ["+2", "/8", "-3", "*7"]

# ages 16..120
age_low = 16
age_high = 120

# variables
m = intvar(age_low, age_high, name="m")  # my age
h = intvar(age_low, age_high, name="h")  # my age

perm1 = intvar(0, n - 1, shape=n, name="perm1")
perm2 = intvar(0, n - 1, shape=n, name="perm2")

# for calculating my age and husband's age
mlist = intvar(1, 1000, shape=n + 1, name="mlist")
hlist = intvar(1, 1000, shape=n + 1, name="hlist")

# constraints
model = Model([AllDifferent(perm1),
               AllDifferent(perm2),

               # same operations in different order
               sum([perm1[i] != perm2[i] for i in range(n)]) > 0,

               # find husbands age, start with my age
               hlist[0] == m,

               # husband's age is last in hlist
               h == hlist[n],

               # checking my age, start with husband's age
               mlist[0] == h,

               # my age is last in mlist
               m == mlist[n],

               # check the operations
               [check(perm1[i], hlist[i], hlist[i + 1]) for i in range(n)],
               [check(perm2[i], mlist[i], mlist[i + 1]) for i in range(n)],

               # Symmetry breaking: I'm younger than husband
               # <SYMMETRY_BREAKING_CONSTRAINT_START>
               # m < h
               # <SYMMETRY_BREAKING_CONSTRAINT_END>
               ])

# Solve
model.solve()

# Print the solution
solution = {
    "m": m.value(),
    "h": h.value()
}
print(json.dumps(solution))
# End of CPMPy script
