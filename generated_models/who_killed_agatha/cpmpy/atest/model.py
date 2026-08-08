from cpmpy import *
import json

# Input data
names = ["Agatha herself", "the butler", "Charles"]

# Decision variables
killer = intvar(0, 2, name="killer")

# Model
model = Model()

# Define variables for who hates whom
# hate[i][j] = 1 if person i hates person j, 0 otherwise
hate = boolvar(shape=(3, 3), name="hate")

# Define variables for who is richer than whom
# richer[i][j] = 1 if person i is richer than person j, 0 otherwise
richer = boolvar(shape=(3, 3), name="richer")

# Constraints
# 1. A killer always hates, and is no richer than his victim (Agatha)
model += [hate[killer, 0] == 1]  # Killer hates Agatha
model += [richer[killer, 0] == 0]  # Killer is not richer than Agatha

# 2. Charles hates no one that Agatha hates
for j in range(3):
    model += [(hate[2, j] == 0) | (hate[0, j] == 0)]

# 3. Agatha hates everybody except the butler
model += [hate[0, 1] == 0]  # Agatha does not hate the butler
model += [hate[0, 0] == 1]  # Agatha hates herself
model += [hate[0, 2] == 1]  # Agatha hates Charles

# 4. The butler hates everyone not richer than Aunt Agatha
for j in range(3):
    model += [hate[1, j] == 1 | (richer[0, j] == 1)]

# 5. The butler hates everyone whom Agatha hates
for j in range(3):
    model += [hate[1, j] == hate[0, j]]

# 6. No one hates everyone
for i in range(3):
    model += [sum(hate[i, :]) < 3]

# Solve the model
model.solve()

# Print the solution
solution = {"killer": killer.value()}
print(json.dumps(solution))