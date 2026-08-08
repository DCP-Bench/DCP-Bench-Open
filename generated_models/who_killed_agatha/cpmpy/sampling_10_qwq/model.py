
import cpmpy as cp
import json

names = ["Agatha herself", "the butler", "Charles"]

# Decision variables
killer = cp.intvar(0, 2, name='killer')
hate = cp.boolvar(shape=(3, 3), name='hate')
wealth = cp.intvar(1, 100, shape=3, name='wealth')  # Wealth bounds are arbitrary but must be integers

model = cp.Model()

# Agatha (0) hates everyone except the butler (1)
for j in range(3):
    if j == 1:
        model += (hate[0, j] == 0)
    else:
        model += (hate[0, j] == 1)

# Butler (1) hates everyone Agatha hates
for j in range(3):
    model += (hate[0, j] == 1).implies(hate[1, j] == 1)

# Butler (1) hates everyone not richer than Agatha (0)
for j in range(3):
    model += (wealth[j] <= wealth[0]).implies(hate[1, j] == 1)

# Charles (2) hates no one Agatha hates
for j in range(3):
    model += (hate[0, j] == 1).implies(hate[2, j] == 0)

# No one hates everyone
for i in range(3):
    model += (cp.sum(hate[i, :]) < 3)

# Killer constraints
model += (hate[killer, 0] == 1)  # Must hate Agatha
model += (wealth[killer] <= wealth[0])  # Must be no richer than Agatha

if model.solve():
    solution = {'killer': int(killer.value())}
    print(json.dumps(solution))
else:
    print("No solution found.")
