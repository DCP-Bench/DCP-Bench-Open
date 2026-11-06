#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/finding_celebrities.py

# Data

#  Adam  knows [Dan,Alice,Peter,Eva],  [2,3,4,5]
#  Dan   knows [Adam,Alice,Peter],     [1,4,5]
#  Eva   knows [Alice,Peter],          [4,5]
#  Alice knows [Peter],                [5]
#  Peter knows [Alice]                 [4]
graph = [
    [1, 1, 1, 1, 1],  # 1
    [1, 1, 0, 1, 1],  # 2
    [0, 0, 1, 1, 1],  # 3
    [0, 0, 0, 1, 1],  # 4
    [0, 0, 0, 1, 1]  # 5
]
# End of data

# Import libraries
from cpmpy import *
import json

model = Model()

# variables
n = len(graph)
celebrities = boolvar(shape=n, name="celebrities")  # 1 if a celebrity
num_celebrities = intvar(1, n, name="num_celebrities")

# constraints
model += (num_celebrities == sum(celebrities))

# All persons know the celebrities,
# and the celebrities only know celebrities.
for i in range(n):
    model += celebrities[i] == (
            (sum([graph[j][i] for j in range(n)]) == n) & (sum([graph[i][j] for j in range(n)]) == num_celebrities))

model.solve()

solution = {"celebrities": celebrities.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
