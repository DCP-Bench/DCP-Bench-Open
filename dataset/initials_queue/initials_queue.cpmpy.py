#!/usr/bin/python3
# Category: hakan_examples
# Source: https://www.hakank.org/cpmpy/initials_queue_problem.py

"""
I noticed something weird about names of the first 10 people in
the queue for a Maths lecture:
[Image of 10 people in a queue.]

Each of them had initials which were an alphabetically ordered
pair of distinct letters from the first five letters of the
alphabet (A,B,C,D,E)! None of the people had the same initials as
any other and no-one shared a letter with the person in front of
them. Mathematician BE was at the front of the queue with CD
right behind, while BD was right at the end of the queue.
Can you use this information to work out the initials of the ten
people in the queue, starting from the front?

Print the queue (queue) of the initials as a list of 10 lists of 2 integers ranging from 0 to 4, representing A to E.
"""

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
