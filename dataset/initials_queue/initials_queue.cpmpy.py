#!/usr/bin/python3
# Category: hakan_examples
# Source: https://www.hakank.org/cpmpy/initials_queue_problem.py

# Import libraries
from cpmpy import *
import json

n = 10

A = 0
B = 1
C = 2
D = 3
E = 4

queue = intvar(A, E, shape=(n, 2), name="queue")

# constraints
model = Model()

# 1. Alphabetically ordered and distinct initials within each person.
for i in range(n):
    model += [queue[i, 0] < queue[i, 1]]

# 2. No two people have the same initials.  AllDifferent on combined initials.
for i in range(n):
    for j in range(i + 1, n):
        model += [(queue[i, 0] != queue[j, 0]) | (queue[i, 1] != queue[j, 1])]

# 3. No shared letters with the person in front.
for i in range(n - 1):
    model += [queue[i, 0] != queue[i + 1, 0]]
    model += [queue[i, 0] != queue[i + 1, 1]]
    model += [queue[i, 1] != queue[i + 1, 0]]
    model += [queue[i, 1] != queue[i + 1, 1]]

# Specific initial assignments based on the problem statement.
model += [queue[0, 0] == 1]  # BE in front (B=1, E=4)
model += [queue[0, 1] == 4]
model += [queue[1, 0] == 2]  # CD right behind (C=2, D=3)
model += [queue[1, 1] == 3]
model += [queue[n - 1, 0] == 1]  # BD at the end (B=1, D=3)
model += [queue[n - 1, 1] == 3]

model.solve()

solution = {
    "queue": queue.value().tolist()
}
print(json.dumps(solution))
