#!/usr/bin/python3
# Category: aplai_course
# Source: http://www.hakank.org/minizinc/subsets_100.mzn

"""
Out of a set of integers, you are given a list of different integers. From
this set A of integers you can always find two disjoint non-empty subsets, S and T, such that the sum of elements
in S equals the sum of elements in T. Note: S union T does not need to be all ten elements of A. Find sets S and T
for the given set A.

Print which elements are in S (in_S) and which elements are in T (in_T), with 2 lists of the same length as A, where 1 means that
the element is in the subset, and 0 means that it is not.
"""

# Data
A = [81, 21, 79, 4, 29, 70, 28, 20, 14, 7]
# End of data

# Import libraries
from cpmpy import *
import json

# Decision variables: 1 if an element is in the subset, 0 otherwise
in_S = boolvar(shape=len(A))
in_T = boolvar(shape=len(A))

# Model setup
model = Model()

# Constraint: sum of elements in S equals sum of elements in T
model += (sum(in_S * A) == sum(in_T * A))

# S and T are disjoint, so there is no element that is in both S and T
model += (sum(in_S * in_T) == 0)

# S and T are non-empty
model += (sum(in_S) > 0)
model += (sum(in_T) > 0)

# Solve
model.solve()

# Print the solution
solution = {"in_S": in_S.value().tolist(), "in_T": in_T.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script