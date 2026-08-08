import cpmpy as cp
import json

# Problem parameters
n = 27
m = 5
series_length = n + 2  # 29 elements: s0, s1, ..., s27, s28

# Decision variables: each s[i] can be any non-negative integer
s = cp.intvar(0, 50, shape=series_length, name="s")

# Create the model
model = cp.Model()

# Constraint 1: s[n+1] = m (s[28] = 5)
model += s[n+1] == m

# Constraint 2: For each i from 0 to n, count(i in S) = s[i]
# This is the self-referential constraint
for i in range(n + 1):  # i = 0, 1, 2, ..., 27
    count_i = cp.sum([s[j] == i for j in range(series_length)])
    model += count_i == s[i]

# Solve the model
if model.solve():
    solution_values = s.value()
    
    # Verification
    def verify_solution(series):
        # Check constraint 1: s[28] = 5
        if series[28] != 5:
            return False, f"s[28] = {series[28]}, expected 5"
        
        # Check constraint 2: self-referential counting
        for i in range(28):  # i = 0 to 27
            count_i = list(series).count(i)
            expected = series[i]
            if count_i != expected:
                return False, f"Value {i} appears {count_i} times, but s[{i}] = {expected}"
        
        return True, "All constraints satisfied"
    
    is_valid, message = verify_solution(solution_values.tolist())
    
    if is_valid:
        # Output the solution in the required JSON format
        solution = {"s": solution_values.tolist()}
        print(json.dumps(solution))
    else:
        print(json.dumps({"error": f"Solution verification failed: {message}"}))
        
else:
    print(json.dumps({"error": "No solution found"}))