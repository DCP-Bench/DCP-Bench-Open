
import cpmpy as cp
import json

stage = 8  # Number of stages

# Decision Variables
wolf = cp.intvar(0, 1, shape=stage, name="wolf")
goat = cp.intvar(0, 1, shape=stage, name="goat")
cabbage = cp.intvar(0, 1, shape=stage, name="cabbage")
boat = cp.intvar(0, 1, shape=stage, name="boat")

model = cp.Model()

# Initial positions: all on starting shore (0)
model += (wolf[0] == 0)
model += (goat[0] == 0)
model += (cabbage[0] == 0)
model += (boat[0] == 0)

# Final positions: all on destination shore (1)
model += (wolf[-1] == 1)
model += (goat[-1] == 1)
model += (cabbage[-1] == 1)
model += (boat[-1] == 1)

# Boat must move to the opposite shore every step
for t in range(stage - 1):
    model += (boat[t + 1] == 1 - boat[t])

# Transition constraints: can only move 0 or 1 items per step
for t in range(stage - 1):
    changes = (
        (wolf[t+1] != wolf[t]) +
        (goat[t+1] != goat[t]) +
        (cabbage[t+1] != cabbage[t])
    )
    model += (changes <= 1)

# Safety constraints: Wolf/Goat and Goat/Cabbage can't be left alone
for t in range(stage):
    # Wolf and Goat must be with the boat if on the same shore
    model += ((wolf[t] == goat[t]).implies(boat[t] == wolf[t]))
    # Goat and Cabbage must be with the boat if on the same shore
    model += ((goat[t] == cabbage[t]).implies(boat[t] == goat[t]))

# Solve and print
if model.solve():
    solution = {
        'wolf_pos': wolf.value().tolist(),
        'goat_pos': goat.value().tolist(),
        'cabbage_pos': cabbage.value().tolist(),
        'boat_pos': boat.value().tolist(),
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
