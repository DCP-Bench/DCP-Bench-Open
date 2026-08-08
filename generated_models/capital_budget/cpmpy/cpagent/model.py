import cpmpy as cp
import json

# Capital Budget Problem
# Maximize NPV subject to budget constraint

# Problem data
npv = [16, 22, 12, 8]  # NPV in thousands of dollars
cost = [5, 7, 4, 3]    # Cost in thousands of dollars  
budget = 14            # Available budget in thousands
n = 4                  # Number of investments

# Decision variables: x[i] = 1 if investment i is chosen, 0 otherwise
x = cp.boolvar(shape=n, name="x")

# Create model
model = cp.Model()

# Constraint: Total cost must not exceed budget
model += cp.sum([x[i] * cost[i] for i in range(n)]) <= budget

# Objective: Maximize total NPV
total_npv = cp.sum([x[i] * npv[i] for i in range(n)])
model.maximize(total_npv)

# Solve the model
if model.solve():
    # Create solution in required format
    solution = {
        "z": int(total_npv.value()),  # NPV in thousands
        "x": x.value().tolist()       # Boolean list for investment choices
    }
    
    # Verification
    def verify_solution(x_sol, expected_npv):
        x_binary = [1 if val else 0 for val in x_sol]
        total_cost_check = sum(x_binary[i] * cost[i] for i in range(4))
        calculated_npv = sum(x_binary[i] * npv[i] for i in range(4))
        
        if total_cost_check > budget:
            return False, f"Budget constraint violated: cost={total_cost_check}, budget={budget}"
        if calculated_npv != expected_npv:
            return False, f"NPV mismatch: calculated={calculated_npv}, expected={expected_npv}"
        return True, "All constraints satisfied"
    
    valid, message = verify_solution(solution["x"], solution["z"])
    assert valid, f"Solution verification failed: {message}"
    
    # Output solution
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))