import cpmpy as cp
import json

# Step 1: Deconstruct & Pre-compute
# This is a system of linear equations problem where we need to find individual costs
# Given constraints:
# paper_hanger + painter = 1100
# painter + plumber = 1700  
# plumber + electrician = 1100
# electrician + carpenter = 3300
# carpenter + mason = 5300
# mason + painter = 3200

# Step 2: Model with CPMpy
# Decision variables - each person's cost
# Using reasonable bounds (costs should be positive and not too large)
paper_hanger = cp.intvar(0, 10000, name="paper_hanger")
painter = cp.intvar(0, 10000, name="painter") 
plumber = cp.intvar(0, 10000, name="plumber")
electrician = cp.intvar(0, 10000, name="electrician")
carpenter = cp.intvar(0, 10000, name="carpenter")
mason = cp.intvar(0, 10000, name="mason")

# Create model
model = cp.Model()

# Add constraints based on the given information
model += paper_hanger + painter == 1100
model += painter + plumber == 1700
model += plumber + electrician == 1100  
model += electrician + carpenter == 3300
model += carpenter + mason == 5300
model += mason + painter == 3200

# Step 3: Solve & Verify
# This is a satisfaction problem (finding any valid solution), so we use model.solve()
if model.solve():
    # Extract solution values
    solution = {
        "paper_hanger": int(paper_hanger.value()),
        "painter": int(painter.value()),
        "plumber": int(plumber.value()),
        "electrician": int(electrician.value()),
        "carpenter": int(carpenter.value()),
        "mason": int(mason.value())
    }
    
    # Verification - check all constraints independently
    def verify_solution(sol):
        ph = sol["paper_hanger"]
        p = sol["painter"] 
        pl = sol["plumber"]
        e = sol["electrician"]
        c = sol["carpenter"]
        m = sol["mason"]
        
        # Check each constraint
        constraints = [
            (ph + p == 1100, "paper_hanger + painter = 1100"),
            (p + pl == 1700, "painter + plumber = 1700"),
            (pl + e == 1100, "plumber + electrician = 1100"),
            (e + c == 3300, "electrician + carpenter = 3300"),
            (c + m == 5300, "carpenter + mason = 5300"),
            (m + p == 3200, "mason + painter = 3200")
        ]
        
        all_satisfied = True
        for constraint, description in constraints:
            if not constraint:
                all_satisfied = False
        
        # Check that all costs are non-negative
        for person, cost in sol.items():
            if cost < 0:
                all_satisfied = False
        
        return all_satisfied
    
    # Verify the solution
    assert verify_solution(solution), "Solution verification failed!"
    
    # Step 4: Output
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))