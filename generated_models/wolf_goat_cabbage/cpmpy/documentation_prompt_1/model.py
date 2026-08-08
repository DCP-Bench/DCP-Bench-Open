
import cpmpy as cp
import json

# Data
stage = 8  # Number of stages
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# Positions: 0 = starting shore, 1 = destination shore
wolf_pos = cp.intvar(0, 1, shape=stage, name="wolf_pos")
goat_pos = cp.intvar(0, 1, shape=stage, name="goat_pos")
cabbage_pos = cp.intvar(0, 1, shape=stage, name="cabbage_pos")
boat_pos = cp.intvar(0, 1, shape=stage, name="boat_pos")

# Constraints
# Initial positions: all on starting shore
model += (wolf_pos[0] == 0)
model += (goat_pos[0] == 0)
model += (cabbage_pos[0] == 0)
model += (boat_pos[0] == 0)

# Final positions: all on destination shore
model += (wolf_pos[-1] == 1)
model += (goat_pos[-1] == 1)
model += (cabbage_pos[-1] == 1)
model += (boat_pos[-1] == 1)

for t in range(stage - 1):
    # The boat moves each stage (cannot stay in place)
    model += (boat_pos[t] != boat_pos[t+1])

    # At each stage, only the farmer and at most one item can move
    # Items can only move if they are on the same side as the boat at time t
    # The farmer always moves with the boat
    # So the difference in position for each item is either 0 or 1 (if moved)
    # The boat moves, so boat_pos[t] != boat_pos[t+1]
    # The item moves if it is on the same side as the boat at time t and moves with the boat

    # Define boolean variables for whether each item moves at step t
    wolf_moves = cp.boolvar(name=f"wolf_moves_{t}")
    goat_moves = cp.boolvar(name=f"goat_moves_{t}")
    cabbage_moves = cp.boolvar(name=f"cabbage_moves_{t}")

    # Item moves if and only if it changes position
    model += (wolf_moves == (wolf_pos[t] != wolf_pos[t+1]))
    model += (goat_moves == (goat_pos[t] != goat_pos[t+1]))
    model += (cabbage_moves == (cabbage_pos[t] != cabbage_pos[t+1]))

    # If item moves, it must be on the same side as the boat at time t
    model += wolf_moves.implies(wolf_pos[t] == boat_pos[t])
    model += goat_moves.implies(goat_pos[t] == boat_pos[t])
    model += cabbage_moves.implies(cabbage_pos[t] == boat_pos[t])

    # At most one item moves with the boat
    model += (cp.sum([wolf_moves, goat_moves, cabbage_moves]) <= 1)

    # Items that do not move stay in the same position
    # (Already enforced by definition of moves variables)

    # Safety constraints: no eating on either shore at any stage
    # If wolf and goat are alone on a shore without the farmer (boat), wolf eats goat
    # If goat and cabbage are alone on a shore without the farmer (boat), goat eats cabbage

    # For each shore (0 and 1), check if wolf and goat alone without farmer
    # wolf and goat on same shore, farmer not on that shore
    for shore in [0, 1]:
        # wolf and goat on shore
        wolf_goat_same_shore = (wolf_pos[t] == shore) & (goat_pos[t] == shore)
        # farmer not on shore
        farmer_not_on_shore = (boat_pos[t] != shore)
        # wolf eats goat forbidden
        model += ~(wolf_goat_same_shore & farmer_not_on_shore)

        # goat and cabbage on shore
        goat_cabbage_same_shore = (goat_pos[t] == shore) & (cabbage_pos[t] == shore)
        # farmer not on shore
        # goat eats cabbage forbidden
        model += ~(goat_cabbage_same_shore & farmer_not_on_shore)

# Also check safety at final stage
for shore in [0, 1]:
    wolf_goat_same_shore = (wolf_pos[-1] == shore) & (goat_pos[-1] == shore)
    farmer_not_on_shore = (boat_pos[-1] != shore)
    model += ~(wolf_goat_same_shore & farmer_not_on_shore)

    goat_cabbage_same_shore = (goat_pos[-1] == shore) & (cabbage_pos[-1] == shore)
    model += ~(goat_cabbage_same_shore & farmer_not_on_shore)

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
