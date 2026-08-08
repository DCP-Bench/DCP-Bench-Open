
import cpmpy as cp
import json

# Data (optional)
stage = 8  # Number of stages
# End of data

# Model definition
model = cp.Model()

# Decision Variables
wolf_pos = cp.intvar(0, 1, shape=stage, name="wolf_pos")
goat_pos = cp.intvar(0, 1, shape=stage, name="goat_pos")
cabbage_pos = cp.intvar(0, 1, shape=stage, name="cabbage_pos")
boat_pos = cp.intvar(0, 1, shape=stage, name="boat_pos")

# Constraints

# Initial and final positions
model += (wolf_pos[0] == 0)
model += (goat_pos[0] == 0)
model += (cabbage_pos[0] == 0)
model += (boat_pos[0] == 0)

model += (wolf_pos[stage-1] == 1)
model += (goat_pos[stage-1] == 1)
model += (cabbage_pos[stage-1] == 1)
model += (boat_pos[stage-1] == 1)

# Boat must move every step and capacity constraints
for t in range(stage - 1):
    # Boat changes side each step
    model += (boat_pos[t] != boat_pos[t+1])

    # At most one item moves with the boat
    change_w = (wolf_pos[t] != wolf_pos[t+1])
    change_g = (goat_pos[t] != goat_pos[t+1])
    change_c = (cabbage_pos[t] != cabbage_pos[t+1])
    model += (cp.sum([change_w, change_g, change_c]) <= 1)

    # If an item changes side, it must be with the boat before and after the move
    model += change_w.implies((wolf_pos[t] == boat_pos[t]) & (wolf_pos[t+1] == boat_pos[t+1]))
    model += change_g.implies((goat_pos[t] == boat_pos[t]) & (goat_pos[t+1] == boat_pos[t+1]))
    model += change_c.implies((cabbage_pos[t] == boat_pos[t]) & (cabbage_pos[t+1] == boat_pos[t+1]))

# Safety constraints at every stage: no wolf with goat without the boat, no goat with cabbage without the boat
for s in range(stage):
    model += ((wolf_pos[s] == goat_pos[s]).implies(wolf_pos[s] == boat_pos[s]))
    model += ((goat_pos[s] == cabbage_pos[s]).implies(goat_pos[s] == boat_pos[s]))

# Objective (optional) - none needed

# Solve and print
if model.solve():
    solution = {
        'wolf_pos': wolf_pos.value().tolist(),
        'goat_pos': goat_pos.value().tolist(),
        'cabbage_pos': cabbage_pos.value().tolist(),
        'boat_pos': boat_pos.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
