
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

# Movement indicator variables for each step (True if that item moves with the boat this step)
move_w = cp.boolvar(shape=stage - 1, name="move_w")
move_g = cp.boolvar(shape=stage - 1, name="move_g")
move_c = cp.boolvar(shape=stage - 1, name="move_c")

# Constraints
# Initial positions: everything at starting shore (0)
model += (wolf[0] == 0)
model += (goat[0] == 0)
model += (cabbage[0] == 0)
model += (boat[0] == 0)

# Final positions: everything at destination shore (1)
model += (wolf[stage - 1] == 1)
model += (goat[stage - 1] == 1)
model += (cabbage[stage - 1] == 1)
model += (boat[stage - 1] == 1)

# Safety constraints at every stage:
# If wolf and goat are together, the boat (farmer) must be with them; otherwise wolf eats goat.
# If goat and cabbage are together, the boat (farmer) must be with them; otherwise goat eats cabbage.
for t in range(stage):
    model += ((wolf[t] == goat[t]).implies(boat[t] == goat[t]))
    model += ((goat[t] == cabbage[t]).implies(boat[t] == goat[t]))

# Transition constraints between successive stages
for t in range(stage - 1):
    # Boat must move each step (farmer crosses each time): boat flips shore
    model += (boat[t] + boat[t + 1] == 1)

    # Define move booleans as "positions differ" (true iff item toggles shore)
    model += (move_w[t] == (wolf[t] + wolf[t + 1] == 1))
    model += (move_g[t] == (goat[t] + goat[t + 1] == 1))
    model += (move_c[t] == (cabbage[t] + cabbage[t + 1] == 1))

    # At most one item can be carried by the boat per crossing
    model += (cp.sum([move_w[t], move_g[t], move_c[t]]) <= 1)

    # If an item moves, it must have been on the same shore as the boat before crossing,
    # and it must end up on the same shore as the boat after crossing.
    # If an item does not move, it stays on the same shore.
    model += ( move_w[t].implies(wolf[t] == boat[t]) )
    model += ( move_w[t].implies(wolf[t + 1] == boat[t + 1]) )
    model += ( (~move_w[t]).implies(wolf[t + 1] == wolf[t]) )

    model += ( move_g[t].implies(goat[t] == boat[t]) )
    model += ( move_g[t].implies(goat[t + 1] == boat[t + 1]) )
    model += ( (~move_g[t]).implies(goat[t + 1] == goat[t]) )

    model += ( move_c[t].implies(cabbage[t] == boat[t]) )
    model += ( move_c[t].implies(cabbage[t + 1] == boat[t + 1]) )
    model += ( (~move_c[t]).implies(cabbage[t + 1] == cabbage[t]) )

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
