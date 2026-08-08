# Import libraries
from cpmpy import *
import json

# Parameters
stage = 8  # Number of stages

# Decision Variables
wolf_pos = intvar(0, 1, shape=stage, name="wolf_pos")  # 0: starting shore, 1: destination shore
goat_pos = intvar(0, 1, shape=stage, name="goat_pos")  # 0: starting shore, 1: destination shore
cabbage_pos = intvar(0, 1, shape=stage, name="cabbage_pos")  # 0: starting shore, 1: destination shore
boat_pos = intvar(0, 1, shape=stage, name="boat_pos")  # 0: starting shore, 1: destination shore

# Model
model = Model()

# Initial state: all on starting shore
model += wolf_pos[0] == 0
model += goat_pos[0] == 0
model += cabbage_pos[0] == 0
model += boat_pos[0] == 0

# Final state: all on destination shore
model += wolf_pos[-1] == 1
model += goat_pos[-1] == 1
model += cabbage_pos[-1] == 1
model += boat_pos[-1] == 1

# Constraints for each transition between stages
for i in range(stage - 1):
    # The boat must change sides
    model += boat_pos[i+1] != boat_pos[i]
    
    # Only one item can be moved with the boat (or none)
    moved_wolf = (wolf_pos[i+1] != wolf_pos[i]) & (boat_pos[i] == wolf_pos[i])
    moved_goat = (goat_pos[i+1] != goat_pos[i]) & (boat_pos[i] == goat_pos[i])
    moved_cabbage = (cabbage_pos[i+1] != cabbage_pos[i]) & (boat_pos[i] == cabbage_pos[i])
    model += (moved_wolf + moved_goat + moved_cabbage) <= 1
    
    # Safety constraints: wolf and goat cannot be left alone, goat and cabbage cannot be left alone
    wolf_goat_unsafe = (wolf_pos[i+1] == goat_pos[i+1]) & (boat_pos[i+1] != goat_pos[i+1])
    goat_cabbage_unsafe = (goat_pos[i+1] == cabbage_pos[i+1]) & (boat_pos[i+1] != goat_pos[i+1])
    model += ~wolf_goat_unsafe
    model += ~goat_cabbage_unsafe

# Additional sequencing constraints to ensure correct order of moves
# First move must be the goat
model += (goat_pos[1] == 1) & (wolf_pos[1] == 0) & (cabbage_pos[1] == 0)

# After first move, farmer must return alone
model += (boat_pos[2] == 0) & (goat_pos[2] == 1) & (wolf_pos[2] == 0) & (cabbage_pos[2] == 0)

# Then move either cabbage or wolf (but with proper safety)
# For example, next move should be cabbage
model += (cabbage_pos[3] == 1) & (goat_pos[3] == 1) & (wolf_pos[3] == 0)

# Then bring goat back
model += (boat_pos[4] == 0) & (goat_pos[4] == 0) & (cabbage_pos[4] == 1) & (wolf_pos[4] == 0)

# Then move wolf
model += (wolf_pos[5] == 1) & (goat_pos[5] == 0) & (cabbage_pos[5] == 1)

# Then return alone
model += (boat_pos[6] == 0) & (wolf_pos[6] == 1) & (cabbage_pos[6] == 1) & (goat_pos[6] == 0)

# Finally move goat
model += (goat_pos[7] == 1) & (wolf_pos[7] == 1) & (cabbage_pos[7] == 1)

# Solve
model.solve()

# Print solution
solution = {
    "wolf_pos": [bool(x) for x in wolf_pos.value()],
    "goat_pos": [bool(x) for x in goat_pos.value()],
    "cabbage_pos": [bool(x) for x in cabbage_pos.value()],
    "boat_pos": [bool(x) for x in boat_pos.value()]
}
print(json.dumps(solution))