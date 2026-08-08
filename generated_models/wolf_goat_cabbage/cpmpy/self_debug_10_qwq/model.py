
import cpmpy as cp
import json

# Decision Variables
wolf_pos = cp.intvar(0, 1, shape=8, name="wolf_pos")
goat_pos = cp.intvar(0, 1, shape=8, name="goat_pos")
cabbage_pos = cp.intvar(0, 1, shape=8, name="cabbage_pos")
boat_pos = cp.intvar(0, 1, shape=8, name="boat_pos")

model = cp.Model()

# Initial state (stage 0)
model += (wolf_pos[0] == 0)
model += (goat_pos[0] == 0)
model += (cabbage_pos[0] == 0)
model += (boat_pos[0] == 0)

# Final state (stage 7)
model += (wolf_pos[7] == 1)
model += (goat_pos[7] == 1)
model += (cabbage_pos[7] == 1)
model += (boat_pos[7] == 1)

# Boat must alternate positions each step
for i in range(1, 8):
    model += (boat_pos[i] != boat_pos[i-1])

# Items can only stay or move with the boat each step
for item in [wolf_pos, goat_pos, cabbage_pos]:
    for i in range(1, 8):
        model += ( (item[i] == item[i-1]) | (item[i] == boat_pos[i]) )

# New constraint: At most one item moves per step
for i in range(1, 8):
    moved = [
        (wolf_pos[i] != wolf_pos[i-1]),
        (goat_pos[i] != goat_pos[i-1]),
        (cabbage_pos[i] != cabbage_pos[i-1])
    ]
    model += (cp.sum(moved) <= 1)  # Allow 0 or 1 items to move

# Safety constraints: no wolf+goat or goat+cabbage on the opposite shore
for i in range(8):
    opposite_shore = 1 - boat_pos[i]
    # Wolf and goat cannot both be on the opposite shore
    model += ( (wolf_pos[i] != opposite_shore) | (goat_pos[i] != opposite_shore) )
    # Goat and cabbage cannot both be on the opposite shore
    model += ( (goat_pos[i] != opposite_shore) | (cabbage_pos[i] != opposite_shore) )

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
