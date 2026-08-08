
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# x: card labels around the circle at positions 0..11 (values 1..12)
x = cp.intvar(1, 12, shape=12, name="x")

# succ: successor position when jumping from position i (values 0..11)
succ = cp.intvar(0, 11, shape=12, name="succ")

# pos: the sequence of visited positions starting from the card labeled 1
pos = cp.intvar(0, 11, shape=12, name="pos")

# Constraints
# x is a permutation of 1..12
model += cp.AllDifferent(x)

# Define successors: from position i you go (i + x[i]) mod 12
for i in range(12):
    model += succ[i] == (i + x[i]) % 12

# Start at the position that holds card 1
model += cp.Element(x, pos[0]) == 1

# Follow successors for 11 jumps to produce 12 visited positions
for t in range(1, 12):
    model += pos[t] == cp.Element(succ, pos[t - 1])

# All visited positions must be distinct (visit every position exactly once)
model += cp.AllDifferent(pos)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
