#!/usr/bin/python3
# Category: csplib
# Source description: https://www.csplib.org/Problems/prob003/
# Model source: https://www.csplib.org/Problems/prob003/models/QuasiGroup.py.html

"""
An order m quasigroup is a Latin square of size m. That is, a $m \\times m$ multiplication table in which each element
occurs once in every row and column. For example,

```
1    2   3   4
4    1   2   3
3    4   1   2
2    3   4   1
```

is an order 4 quasigroup. A quasigroup can be specified by a set and a binary multiplication operator, \\* defined over
this set. Quasigroup existence problems determine the existence or non-existence of quasigroups of a given size with
additional properties. Certain existence problems are of sufficient interest that a naming scheme has been invented
for them. We define two new relations, \\*321 and \\*312 by $a \\*321 b = c$ iff $c\\*b=a$ and
$a \\*312 b = c$ iff $b\\*c=a$.

QG3.m problems are order m quasigroups for which $(a\\*b)\\*(b\\*a) = a$.
We only consider the QG3.m problem for this task.

Print the quasigroup (quasigroup) as a list of lists of integers from 0 to m-1.
"""

# Data
m = 8  # Order of the quasigroup
# End of data

# Import libraries
from cpmpy import *
import json

# Decision Variables
quasigroup = intvar(0, m - 1, shape=(m, m), name="quasigroup")

# Model
model = Model()

# Each element occurs once in every row
for i in range(m):
    model += AllDifferent(quasigroup[i, :])

# Each element occurs once in every column
for j in range(m):
    model += AllDifferent(quasigroup[:, j])

# QG3.m property: (a*b)*(b*a) = a
for a in range(m):
    for b in range(m):
        model += quasigroup[quasigroup[a, b], quasigroup[b, a]] == a


# Solve
model.solve()

# Print
solution = {"quasigroup": quasigroup.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
