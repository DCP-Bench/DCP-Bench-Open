
import cpmpy as cp
import json

# Data
stage = 8  # Number of stages
# End of data

# Model definition
model = cp.Model()

# Decision Variables: positions at each stage (0=start shore, 1=destination shore)
wolf_pos = cp.intvar(0, 1, shape=stage, name="wolf_pos")
goat_pos = cp.intvar(0, 1, shape=stage, name="goat_pos")
cabbage_pos = cp.intvar(0, 1, shape=stage, name="cabbage_pos")
boat_pos = cp.intvar(0, 1, shape=stage, name="boat_pos")

# For each transition, whether an item moves (wolf, goat, cabbage)
# moved[s,0] for wolf moving between s and s+1, etc.
moved = cp.boolvar((stage - 1, 3), name="moved")

# Initial positions: all at starting shore (0)
model += (wolf_pos[0] == 0)
model += (goat_pos[0] == 0)
model += (cabbage_pos[0] == 0)
model += (boat_pos[0] == 0)

# Goal positions: all at destination shore (1)
model += (wolf_pos[stage - 1] == 1)
model += (goat_pos[stage - 1] == 1)
model += (cabbage_pos[stage - 1] == 1)
model += (boat_pos[stage - 1] == 1)

# Constraints for each move between stage s and s+1
for s in range(stage - 1):
    # Boat must move each time
    model += (boat_pos[s] != boat_pos[s + 1])
    
    # Link movement indicators for wolf, goat, cabbage
    # moved[s,0] <-> (wolf_pos[s] != wolf_pos[s+1]), etc.
    model += ((wolf_pos[s] != wolf_pos[s + 1]) == moved[s, 0])
    model += ((goat_pos[s] != goat_pos[s + 1]) == moved[s, 1])
    model += ((cabbage_pos[s] != cabbage_pos[s + 1]) == moved[s, 2])
    
    # At most one item moves with the boat
    model += (cp.sum(moved[s, :]) <= 1)
    
    # If an item moves, it must be on the same shore as the boat before and after
    # Wolf
    model += cp.implies(moved[s, 0], wolf_pos[s] == boat_pos[s])
    model += cp.implies(moved[s, 0], wolf_pos[s + 1] == boat_pos[s + 1])
    # Goat
    model += cp.implies(moved[s, 1], goat_pos[s] == boat_pos[s])
    model += cp.implies(moved[s, 1], goat_pos[s + 1] == boat_pos[s + 1])
    # Cabbage
    model += cp.implies(moved[s, 2], cabbage_pos[s] == boat_pos[s])
    model += cp.implies(moved[s, 2], cabbage_pos[s + 1] == boat_pos[s + 1])
    
    # Safety constraints at stage s: no eating when farmer (boat) is absent
    # If goat and cabbage alone without boat => forbidden
    model += cp.implies(goat_pos[s] == cabbage_pos[s],
                         boat_pos[s] == goat_pos[s])
    # If wolf and goat alone without boat => forbidden
    model += cp.implies(wolf_pos[s] == goat_pos[s],
                         boat_pos[s] == goat_pos[s])

# Also apply safety at the final stage
model += cp.implies(goat_pos[stage - 1] == cabbage_pos[stage - 1],
                     boat_pos[stage - 1] == goat_pos[stage - 1])
model += cp.implies(wolf_pos[stage - 1] == goat_pos[stage - 1],
                     boat_pos[stage - 1] == goat_pos[stage - 1])

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
