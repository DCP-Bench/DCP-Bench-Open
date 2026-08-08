
import cpmpy as cp
import json

stage = 8  # Number of stages

# Model definition
model = cp.Model()

# Decision Variables
# Positions of wolf, goat, cabbage, boat at each stage: 0=starting shore, 1=destination shore
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

for t in range(stage-1):
    # The boat moves between shores each stage (0->1 or 1->0)
    model += (boat_pos[t+1] != boat_pos[t])

    # Only the farmer (boat) and zero or one item moves together
    # So at each step, at most one of wolf, goat, cabbage moves, and only if it is on the same side as the boat
    # Compute which items move at this stage
    wolf_move = wolf_pos[t+1] != wolf_pos[t]
    goat_move = goat_pos[t+1] != goat_pos[t]
    cabbage_move = cabbage_pos[t+1] != cabbage_pos[t]

    # Each moved item must be on the same side as the boat before crossing
    model += wolf_move.implies(wolf_pos[t] == boat_pos[t])
    model += goat_move.implies(goat_pos[t] == boat_pos[t])
    model += cabbage_move.implies(cabbage_pos[t] == boat_pos[t])

    # At most one item moves per crossing (boat always moves)
    model += (wolf_move + goat_move + cabbage_move <= 1)

    # Items that do not move remain in the same position
    model += wolf_move.implies(wolf_pos[t+1] != wolf_pos[t])
    model += (~wolf_move).implies(wolf_pos[t+1] == wolf_pos[t])
    model += goat_move.implies(goat_pos[t+1] != goat_pos[t])
    model += (~goat_move).implies(goat_pos[t+1] == goat_pos[t])
    model += cabbage_move.implies(cabbage_pos[t+1] != cabbage_pos[t])
    model += (~cabbage_move).implies(cabbage_pos[t+1] == cabbage_pos[t])

    # Safety constraints at stage t+1 (after crossing)
    # If wolf and goat alone on one shore without farmer => goat eaten
    # If goat and cabbage alone on one shore without farmer => cabbage eaten
    # So for each shore, if wolf and goat both there and farmer not there => forbidden
    # If goat and cabbage both there and farmer not there => forbidden

    # Shore 0 safety
    shore0_wolf = (wolf_pos[t+1] == 0)
    shore0_goat = (goat_pos[t+1] == 0)
    shore0_cabbage = (cabbage_pos[t+1] == 0)
    shore0_boat = (boat_pos[t+1] == 0)

    # Shore 1 safety
    shore1_wolf = (wolf_pos[t+1] == 1)
    shore1_goat = (goat_pos[t+1] == 1)
    shore1_cabbage = (cabbage_pos[t+1] == 1)
    shore1_boat = (boat_pos[t+1] == 1)

    # Goat and wolf alone on shore0 without farmer
    model += ~((shore0_wolf & shore0_goat & ~shore0_boat))
    # Goat and cabbage alone on shore0 without farmer
    model += ~((shore0_goat & shore0_cabbage & ~shore0_boat))

    # Goat and wolf alone on shore1 without farmer
    model += ~((shore1_wolf & shore1_goat & ~shore1_boat))
    # Goat and cabbage alone on shore1 without farmer
    model += ~((shore1_goat & shore1_cabbage & ~shore1_boat))

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
