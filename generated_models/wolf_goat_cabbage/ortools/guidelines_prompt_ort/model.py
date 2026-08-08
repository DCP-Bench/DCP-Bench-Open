
from ortools.sat.python import cp_model
import json

# Input data
stage = 8  # Number of stages

# Create the model
model = cp_model.CpModel()
N = stage

# Decision variables: positions at each stage (0 = starting shore, 1 = destination shore)
wolf_pos = [model.NewBoolVar(f'wolf_pos[{t}]') for t in range(N)]
goat_pos = [model.NewBoolVar(f'goat_pos[{t}]') for t in range(N)]
cabbage_pos = [model.NewBoolVar(f'cabbage_pos[{t}]') for t in range(N)]
boat_pos = [model.NewBoolVar(f'boat_pos[{t}]') for t in range(N)]

# Travel indicators: whether an item travels with the farmer on the boat between stage t and t+1
travel_wolf = [model.NewBoolVar(f'travel_wolf[{t}]') for t in range(N - 1)]
travel_goat = [model.NewBoolVar(f'travel_goat[{t}]') for t in range(N - 1)]
travel_cabbage = [model.NewBoolVar(f'travel_cabbage[{t}]') for t in range(N - 1)]

# 1) Initial positions: all on starting shore (0)
model.Add(wolf_pos[0] == 0)
model.Add(goat_pos[0] == 0)
model.Add(cabbage_pos[0] == 0)
model.Add(boat_pos[0] == 0)

# 2) Final positions: all on destination shore (1)
model.Add(wolf_pos[N - 1] == 1)
model.Add(goat_pos[N - 1] == 1)
model.Add(cabbage_pos[N - 1] == 1)
model.Add(boat_pos[N - 1] == 1)

# 3) Transition constraints between stages
for t in range(N - 1):
    # a) The boat must move (flip side) each time
    #    boat_pos[t] + boat_pos[t+1] == 1 ensures one is 0 and the other is 1
    model.Add(boat_pos[t] + boat_pos[t + 1] == 1)

    # b) At most one item can travel with the boat
    model.Add(travel_wolf[t] + travel_goat[t] + travel_cabbage[t] <= 1)

    # c) For each item, link travel to movement and availability
    for item_pos, travel in [
        (wolf_pos, travel_wolf[t]),
        (goat_pos, travel_goat[t]),
        (cabbage_pos, travel_cabbage[t])
    ]:
        # If the item travels, it must be on the same side as the boat at stage t
        model.Add(item_pos[t] == boat_pos[t]).OnlyEnforceIf(travel)
        # If the item travels, its position flips between t and t+1
        model.Add(item_pos[t] != item_pos[t + 1]).OnlyEnforceIf(travel)
        # If the item does not travel, its position stays the same
        model.Add(item_pos[t] == item_pos[t + 1]).OnlyEnforceIf(travel.Not())

# 4) Safety constraints: prevent eating situations at each stage
for t in range(N):
    W = wolf_pos[t]
    G = goat_pos[t]
    C = cabbage_pos[t]
    B = boat_pos[t]
    # Wolf eats goat if together without farmer
    # Forbid (W=G=0 and B=1) and (W=G=1 and B=0)
    model.AddBoolOr([W, G, B.Not()])    # forbids W=0, G=0, B=1
    model.AddBoolOr([W.Not(), G.Not(), B])  # forbids W=1, G=1, B=0
    # Goat eats cabbage if together without farmer
    model.AddBoolOr([G, C, B.Not()])    # forbids G=0, C=0, B=1
    model.AddBoolOr([G.Not(), C.Not(), B])  # forbids G=1, C=1, B=0

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'wolf_pos': [solver.Value(wolf_pos[t]) for t in range(N)],
        'goat_pos': [solver.Value(goat_pos[t]) for t in range(N)],
        'cabbage_pos': [solver.Value(cabbage_pos[t]) for t in range(N)],
        'boat_pos': [solver.Value(boat_pos[t]) for t in range(N)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
