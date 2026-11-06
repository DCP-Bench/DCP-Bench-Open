#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/cabling.py
# Source description: https://yurichev.com/blog/cabling_Z3/
# Misc: http://www.hakank.org/cpmpy/cpmpy_hakank.py

# Data
n = 8
devices = ["A", "B", "C", "D", "E", "F", "G", "H"]
cable_struct = [["A", "H", 1],
                ["A", "E", 2],
                ["B", "F", 4],
                ["C", "G", 1],
                ["C", "D", 1],
                ["C", "E", 1],
                ["D", "H", 3],
                ["G", "H", 1]]
# End of data

# Import libraries
from cpmpy import *
import json

model = Model()

device_map = {name: i for i, name in enumerate(devices)}
cable_struct_int = [[device_map[c[0]], device_map[c[1]], c[2]] for c in cable_struct]

x = intvar(0, n - 1, shape=n, name="x")  # position of the device in the rack
t = intvar(1, n * n, shape=len(cable_struct_int), name="t")  # cable lengths
final_sum = intvar(0, n * n * sum([c[2] for c in cable_struct_int]), name="final_sum")  # sum of all cable lengths

# all "devices" has distinct positions in rack:
model += AllDifferent(x)
model += final_sum == sum(t)

for i in range(len(cable_struct_int)):
    a, b, num = cable_struct_int[i]
    model += [t[i] == abs(x[a] - x[b]) * num]

model.minimize(final_sum)

# Solve
model.solve()

# Print the solution
solution = {"final_sum": final_sum.value()}
print(json.dumps(solution))
# End of CPMPy script