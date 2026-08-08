from cpmpy import *
import json

# Parameters
n_guests = 6  # Number of guests

# Guest names in order: Andrew, Betty, Cara, Dave, Erica, Frank
# Index mapping: 0 -> Andrew, 1 -> Betty, 2 -> Cara, 3 -> Dave, 4 -> Erica, 5 -> Frank

# Compatibility matrix: compatibility[i][j] = 1 if guest i can sit next to guest j, else 0
compatibility = [
    [0, 0, 0, 1, 0, 1],  # Andrew can sit next to Dave (3) and Frank (5)
    [0, 0, 1, 0, 1, 0],  # Betty can sit next to Cara (2) and Erica (4)
    [0, 1, 0, 0, 0, 1],  # Cara can sit next to Betty (1) and Frank (5)
    [1, 0, 0, 0, 1, 0],  # Dave can sit next to Andrew (0) and Erica (4)
    [0, 1, 0, 1, 0, 0],  # Erica can sit next to Betty (1) and Dave (3)
    [1, 0, 1, 0, 0, 0]   # Frank can sit next to Andrew (0) and Cara (2)
]

# Decision variables
x = intvar(0, n_guests - 1, shape=n_guests, name="x")

# Model
model = Model()

# All guests must be seated exactly once
model += [AllDifferent(x)]

# Create a symbolic compatibility matrix using cpm_array
compatibility = cpm_array(compatibility)

# Minimize the number of conflicts
conflicts = 0
for i in range(n_guests):
    left = x[(i - 1) % n_guests]
    right = x[(i + 1) % n_guests]
    # Only count each conflict once
    conflicts += 1 - compatibility[x[i], left]

model.minimize(conflicts)

# Solve the model
model.solve()

# Print the solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))