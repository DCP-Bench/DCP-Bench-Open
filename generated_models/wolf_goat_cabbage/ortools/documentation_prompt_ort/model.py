from ortools.sat.python import cp_model
import json

# Input data
stage = 8  # Number of stages

# Model definition
model = cp_model.CpModel()

# Variables: positions of wolf, goat, cabbage, and boat at each stage
# 0 = starting shore, 1 = destination shore
wolf_pos = [model.NewIntVar(0, 1, f'wolf_pos_{i}') for i in range(stage)]
goat_pos = [model.NewIntVar(0, 1, f'goat_pos_{i}') for i in range(stage)]
cabbage_pos = [model.NewIntVar(0, 1, f'cabbage_pos_{i}') for i in range(stage)]
boat_pos = [model.NewIntVar(0, 1, f'boat_pos_{i}') for i in range(stage)]

# Initial conditions: all start on the starting shore (0)
model.Add(wolf_pos[0] == 0)
model.Add(goat_pos[0] == 0)
model.Add(cabbage_pos[0] == 0)
model.Add(boat_pos[0] == 0)

# Final conditions: all must be on the destination shore (1)
model.Add(wolf_pos[stage - 1] == 1)
model.Add(goat_pos[stage - 1] == 1)
model.Add(cabbage_pos[stage - 1] == 1)
model.Add(boat_pos[stage - 1] == 1)

for i in range(stage - 1):
    # The boat must move at each stage (change position)
    model.Add(boat_pos[i] != boat_pos[i + 1])

    # At most one item can move with the boat (or none)
    # An item moves if its position changes between stages
    wolf_move = model.NewBoolVar(f'wolf_move_{i}')
    goat_move = model.NewBoolVar(f'goat_move_{i}')
    cabbage_move = model.NewBoolVar(f'cabbage_move_{i}')

    model.Add(wolf_pos[i] != wolf_pos[i + 1]).OnlyEnforceIf(wolf_move)
    model.Add(wolf_pos[i] == wolf_pos[i + 1]).OnlyEnforceIf(wolf_move.Not())

    model.Add(goat_pos[i] != goat_pos[i + 1]).OnlyEnforceIf(goat_move)
    model.Add(goat_pos[i] == goat_pos[i + 1]).OnlyEnforceIf(goat_move.Not())

    model.Add(cabbage_pos[i] != cabbage_pos[i + 1]).OnlyEnforceIf(cabbage_move)
    model.Add(cabbage_pos[i] == cabbage_pos[i + 1]).OnlyEnforceIf(cabbage_move.Not())

    # The boat and the item(s) that move must be on the same shore at stage i
    # If an item moves, it must be on the same shore as the boat at stage i
    model.Add(wolf_pos[i] == boat_pos[i]).OnlyEnforceIf(wolf_move)
    model.Add(goat_pos[i] == boat_pos[i]).OnlyEnforceIf(goat_move)
    model.Add(cabbage_pos[i] == boat_pos[i]).OnlyEnforceIf(cabbage_move)

    # At most one item moves with the boat
    model.Add(wolf_move + goat_move + cabbage_move <= 1)

    # Items that do not move stay on the same shore
    # Already enforced by the definition of move variables

    # Safety constraints: no item gets eaten when farmer is not present
    # Farmer is with the boat, so check the shore without the boat
    # For stage i+1 (after move), check the shore without the boat
    # If wolf and goat alone on a shore without farmer, goat eaten
    # If goat and cabbage alone on a shore without farmer, cabbage eaten

    # Define shore without boat at stage i+1
    shore_without_boat = 1 - solver_value := boat_pos[i + 1]

    # We cannot use solver.Value() here, so we use constraints:
    # For stage i+1:
    # If wolf and goat on same shore without boat, and boat not there, invalid
    # Similarly for goat and cabbage

    # Create boolean variables for positions at stage i+1
    wolf_at_shore = model.NewBoolVar(f'wolf_at_shore_{i+1}')
    goat_at_shore = model.NewBoolVar(f'goat_at_shore_{i+1}')
    cabbage_at_shore = model.NewBoolVar(f'cabbage_at_shore_{i+1}')
    boat_at_shore = boat_pos[i + 1]

    model.Add(wolf_pos[i + 1] == 1).OnlyEnforceIf(wolf_at_shore)
    model.Add(wolf_pos[i + 1] == 0).OnlyEnforceIf(wolf_at_shore.Not())

    model.Add(goat_pos[i + 1] == 1).OnlyEnforceIf(goat_at_shore)
    model.Add(goat_pos[i + 1] == 0).OnlyEnforceIf(goat_at_shore.Not())

    model.Add(cabbage_pos[i + 1] == 1).OnlyEnforceIf(cabbage_at_shore)
    model.Add(cabbage_pos[i + 1] == 0).OnlyEnforceIf(cabbage_at_shore.Not())

    # The shore without boat is 1 - boat_pos[i+1]
    # So wolf_at_shore and goat_at_shore on shore without boat means:
    # (wolf_pos[i+1] == shore_without_boat) and (goat_pos[i+1] == shore_without_boat)
    # We can express this as:
    # wolf_at_shore_without_boat = (wolf_pos[i+1] == 1 - boat_pos[i+1])
    # goat_at_shore_without_boat = (goat_pos[i+1] == 1 - boat_pos[i+1])
    # Similarly for cabbage

    # Create boolean variables for wolf, goat, cabbage on shore without boat
    wolf_without_boat = model.NewBoolVar(f'wolf_without_boat_{i+1}')
    goat_without_boat = model.NewBoolVar(f'goat_without_boat_{i+1}')
    cabbage_without_boat = model.NewBoolVar(f'cabbage_without_boat_{i+1}')

    # wolf_without_boat == 1 if wolf_pos[i+1] == 1 - boat_pos[i+1]
    model.Add(wolf_pos[i + 1] == 1 - boat_pos[i + 1]).OnlyEnforceIf(wolf_without_boat)
    model.Add(wolf_pos[i + 1] != 1 - boat_pos[i + 1]).OnlyEnforceIf(wolf_without_boat.Not())

    model.Add(goat_pos[i + 1] == 1 - boat_pos[i + 1]).OnlyEnforceIf(goat_without_boat)
    model.Add(goat_pos[i + 1] != 1 - boat_pos[i + 1]).OnlyEnforceIf(goat_without_boat.Not())

    model.Add(cabbage_pos[i + 1] == 1 - boat_pos[i + 1]).OnlyEnforceIf(cabbage_without_boat)
    model.Add(cabbage_pos[i + 1] != 1 - boat_pos[i + 1]).OnlyEnforceIf(cabbage_without_boat.Not())

    # If wolf and goat alone on shore without boat, goat eaten -> invalid
    # So not (wolf_without_boat and goat_without_boat and not farmer)
    # Farmer is boat, so boat not on that shore means shore without boat
    # So if wolf_without_boat and goat_without_boat then invalid
    model.AddBoolOr([wolf_without_boat.Not(), goat_without_boat.Not()])

    # If goat and cabbage alone on shore without boat, cabbage eaten -> invalid
    model.AddBoolOr([goat_without_boat.Not(), cabbage_without_boat.Not()])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'wolf_pos': [solver.Value(w) for w in wolf_pos],
        'goat_pos': [solver.Value(g) for g in goat_pos],
        'cabbage_pos': [solver.Value(c) for c in cabbage_pos],
        'boat_pos': [solver.Value(b) for b in boat_pos]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")