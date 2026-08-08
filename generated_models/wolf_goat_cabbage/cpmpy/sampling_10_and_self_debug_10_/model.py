
import cpmpy as cp
import json

# Data
stage = 8  # Number of stages
# End of data

# Model definition
model = cp.Model()

# Decision Variables: positions over time (0 = starting shore, 1 = destination shore)
wolf = cp.intvar(0, 1, shape=stage, name="wolf")
goat = cp.intvar(0, 1, shape=stage, name="goat")
cabbage = cp.intvar(0, 1, shape=stage, name="cabbage")
boat = cp.intvar(0, 1, shape=stage, name="boat")

# Moved indicators for each crossing (stage-1 transitions)
mw = cp.boolvar(shape=stage-1, name="mw")  # wolf moved at transition t
mg = cp.boolvar(shape=stage-1, name="mg")  # goat moved
mc = cp.boolvar(shape=stage-1, name="mc")  # cabbage moved

# Constraints
# Initial positions: all at starting shore (0)
model += (wolf[0] == 0)
model += (goat[0] == 0)
model += (cabbage[0] == 0)
model += (boat[0] == 0)

# Final positions: all at destination shore (1)
model += (wolf[stage-1] == 1)
model += (goat[stage-1] == 1)
model += (cabbage[stage-1] == 1)
model += (boat[stage-1] == 1)

# Safety constraints at every stage:
# If wolf and goat are together, the boat (farmer) must be present;
# If goat and cabbage are together, the boat must be present.
for t in range(stage):
    model += ( (wolf[t] == goat[t]).implies(boat[t] == wolf[t]) )
    model += ( (goat[t] == cabbage[t]).implies(boat[t] == goat[t]) )

# Transition constraints between consecutive stages
for t in range(stage - 1):
    # Boat crosses each transition (farmer always moves)
    model += (boat[t] != boat[t+1])

    # Define moved booleans as whether item changes side
    model += (mw[t] == (wolf[t] != wolf[t+1]))
    model += (mg[t] == (goat[t] != goat[t+1]))
    model += (mc[t] == (cabbage[t] != cabbage[t+1]))

    # At most one item can be taken in the boat
    model += (cp.sum([mw[t], mg[t], mc[t]]) <= 1)

    # If an item is moved, it must be on the same side as the boat before crossing
    # and end up on the boat's side after crossing.
    model += ( mw[t].implies(wolf[t] == boat[t]) )
    model += ( mw[t].implies(wolf[t+1] == boat[t+1]) )
    model += ( mg[t].implies(goat[t] == boat[t]) )
    model += ( mg[t].implies(goat[t+1] == boat[t+1]) )
    model += ( mc[t].implies(cabbage[t] == boat[t]) )
    model += ( mc[t].implies(cabbage[t+1] == boat[t+1]) )

    # If an item is not moved, it must stay on the same side
    model += ( (~mw[t]).implies(wolf[t] == wolf[t+1]) )
    model += ( (~mg[t]).implies(goat[t] == goat[t+1]) )
    model += ( (~mc[t]).implies(cabbage[t] == cabbage[t+1]) )

# Solve and print
if model.solve():
    solution = {
        'wolf_pos': wolf.value().tolist(),
        'goat_pos': goat.value().tolist(),
        'cabbage_pos': cabbage.value().tolist(),
        'boat_pos': boat.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
