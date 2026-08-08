import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# Wolf, Goat, and Cabbage river crossing puzzle
# - 8 stages (time steps)
# - Each entity can be on shore 0 (start) or shore 1 (destination)
# - Constraints:
#   1. Wolf and goat cannot be alone together (without farmer)
#   2. Goat and cabbage cannot be alone together (without farmer)
#   3. Farmer is always with the boat
#   4. Only farmer can move items (boat constraint)
#   5. At most one item can move with farmer per step
#   6. Start: all on shore 0, End: all on shore 1

# Step 2: Model with CPMpy
stages = 8

# Decision variables: position of each entity at each stage
# 0 = starting shore, 1 = destination shore
wolf_pos = cp.boolvar(shape=stages, name="wolf_pos")
goat_pos = cp.boolvar(shape=stages, name="goat_pos") 
cabbage_pos = cp.boolvar(shape=stages, name="cabbage_pos")
boat_pos = cp.boolvar(shape=stages, name="boat_pos")  # farmer is always with boat

model = cp.Model()

# Initial conditions: all start on shore 0
model += wolf_pos[0] == 0
model += goat_pos[0] == 0
model += cabbage_pos[0] == 0
model += boat_pos[0] == 0

# Final conditions: all end on shore 1
model += wolf_pos[stages-1] == 1
model += goat_pos[stages-1] == 1
model += cabbage_pos[stages-1] == 1
model += boat_pos[stages-1] == 1

# Movement constraints: only farmer (boat) can transport items
for t in range(1, stages):
    # If wolf moves, boat must move
    model += (wolf_pos[t] != wolf_pos[t-1]).implies(boat_pos[t] != boat_pos[t-1])
    
    # If goat moves, boat must move  
    model += (goat_pos[t] != goat_pos[t-1]).implies(boat_pos[t] != boat_pos[t-1])
    
    # If cabbage moves, boat must move
    model += (cabbage_pos[t] != cabbage_pos[t-1]).implies(boat_pos[t] != boat_pos[t-1])
    
    # At most one item can move with the boat at each step
    wolf_moved = (wolf_pos[t] != wolf_pos[t-1])
    goat_moved = (goat_pos[t] != goat_pos[t-1])
    cabbage_moved = (cabbage_pos[t] != cabbage_pos[t-1])
    
    model += wolf_moved + goat_moved + cabbage_moved <= 1

# Safety constraints: prevent conflicts when farmer is not present
for t in range(stages):
    # Wolf and goat cannot be alone together (both on same side, farmer on other side)
    wolf_goat_together = (wolf_pos[t] == goat_pos[t])
    farmer_elsewhere = (boat_pos[t] != wolf_pos[t])
    model += ~(wolf_goat_together & farmer_elsewhere)
    
    # Goat and cabbage cannot be alone together
    goat_cabbage_together = (goat_pos[t] == cabbage_pos[t])
    farmer_elsewhere_2 = (boat_pos[t] != goat_pos[t])
    model += ~(goat_cabbage_together & farmer_elsewhere_2)

# Step 3: Solve and verify
if model.solve():
    # Extract solution
    wolf_solution = [int(x) for x in wolf_pos.value()]
    goat_solution = [int(x) for x in goat_pos.value()]
    cabbage_solution = [int(x) for x in cabbage_pos.value()]
    boat_solution = [int(x) for x in boat_pos.value()]
    
    solution = {
        "wolf_pos": wolf_solution,
        "goat_pos": goat_solution,
        "cabbage_pos": cabbage_solution,
        "boat_pos": boat_solution
    }
    
    # Verification
    def verify_solution(sol):
        wolf_pos = sol["wolf_pos"]
        goat_pos = sol["goat_pos"] 
        cabbage_pos = sol["cabbage_pos"]
        boat_pos = sol["boat_pos"]
        
        # 1. Structural verification
        if len(wolf_pos) != stages or len(goat_pos) != stages or len(cabbage_pos) != stages or len(boat_pos) != stages:
            return False, "Wrong number of stages"
        
        # 2. Initial and final conditions
        if not (wolf_pos[0] == 0 and goat_pos[0] == 0 and cabbage_pos[0] == 0 and boat_pos[0] == 0):
            return False, "Initial condition violated"
        
        if not (wolf_pos[-1] == 1 and goat_pos[-1] == 1 and cabbage_pos[-1] == 1 and boat_pos[-1] == 1):
            return False, "Final condition violated"
        
        # 3. Movement constraints
        for t in range(1, stages):
            movements = 0
            if wolf_pos[t] != wolf_pos[t-1]:
                movements += 1
                if boat_pos[t] == boat_pos[t-1]:
                    return False, f"Wolf moved at stage {t} but boat didn't"
            
            if goat_pos[t] != goat_pos[t-1]:
                movements += 1
                if boat_pos[t] == boat_pos[t-1]:
                    return False, f"Goat moved at stage {t} but boat didn't"
            
            if cabbage_pos[t] != cabbage_pos[t-1]:
                movements += 1
                if boat_pos[t] == boat_pos[t-1]:
                    return False, f"Cabbage moved at stage {t} but boat didn't"
            
            if movements > 1:
                return False, f"Too many items moved at stage {t}"
        
        # 4. Safety constraints
        for t in range(stages):
            if wolf_pos[t] == goat_pos[t] and boat_pos[t] != wolf_pos[t]:
                return False, f"Wolf and goat alone together at stage {t}"
            
            if goat_pos[t] == cabbage_pos[t] and boat_pos[t] != goat_pos[t]:
                return False, f"Goat and cabbage alone together at stage {t}"
        
        return True, "All constraints satisfied"
    
    valid, msg = verify_solution(solution)
    assert valid, f"Verification failed: {msg}"
    
    # Step 4: Output
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))