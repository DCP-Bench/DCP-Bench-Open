#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/autoref.py
# Misc: http://www.hakank.org/cpmpy/cpmpy_hakank.py

"""
Given an integer n > 0 and an integer m >= 0, find a non-empty finite series S=(s0, s1, ..., sn, sn+1) such that (
1) there are si occurrences of i in S for each integer i ranging from 0 to n, and (2) sn+1=m.

Print the series S (s).
"""

# Data
n = 27
m = 5
# End of data

# Import libraries
from cpmpy import *
import json


def count(a, val, c):
    """
    count(a,val,c)

    c is the number of occurrences of val in array a.
    """
    return [c == sum([a[i] == val for i in range(len(a))])]


def global_cardinality_count(a, gcc):
    """
    global_cardinality_count(a, gcc)

    Global cardinality count: Collect the number of occurrences of each value 0..a.ub
    in gcc. The array gcc must be of length 0..ub.
    """
    n = len(a)
    ub = max([a[i].ub for i in range(n)])
    constraints = []
    for i in range(ub + 1):
        constraints += [count(a, i, gcc[i])]

    return constraints


def autoref(s):
    """
    autoref(s)
    Ensure that the number of occurrences of i in s is s[i].
    s should be an array of 0..n+1
    """
    return [global_cardinality_count(s, s)]


# Decision Variables
s = intvar(0, n, shape=n + 2, name="s")

# Model
model = Model(s[n + 1] == m, autoref(s))

# Solve the model
model.solve()

# Print the solution
solution = {"s": s.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
