#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/euler2.py

# Import libraries
from cpmpy import *
import json

n = 35
f = intvar(0, 10000000, shape=n + 1)
x = boolvar(shape=n + 1)
res = intvar(0, 100000000)

model = Model([
    res == sum([x[i] * f[i] for i in range(1, n + 1)]),
    f[0] == 0,
    f[1] == 1,
    f[2] == 1,
    x[0] == 0,
    [f[i] == f[i - 1] + f[i - 2] for i in range(3, n + 1)],

    # only even valued < 4000000
    [((f[i] % 2 == 0) & (f[i] < 4000000)) == (x[i] == 1) for i in range(1, n + 1)]
])

model.solve()

solution = {"res": res.value()}
print(json.dumps(solution))
# End of CPMPy script
