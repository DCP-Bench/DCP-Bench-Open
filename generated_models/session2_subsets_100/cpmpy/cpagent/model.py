import cpmpy as cp
import json

# Step 1: Problem analysis
# Given set A of 10 integers: [81, 21, 79, 4, 29, 70, 28, 20, 14, 7]
# Find two disjoint non-empty subsets S and T such that sum(S) = sum(T)
# Output: binary arrays indicating membership in S and T

A = [81, 21, 79, 4, 29, 70, 28, 20, 14, 7]
n = len(A)

# Step 2: Model with CPMpy
model = cp.Model()

# Decision variables: boolean variables for subset membership
in_S = cp.boolvar(shape=n, name="in_S")  # in_S[i] = 1 if A[i] is in subset S
in_T = cp.boolvar(shape=n, name="in_T")  # in_T[i] = 1 if A[i] is in subset T

# Step 3: Add constraints

# Constraint 1: S and T are disjoint (no element can be in both)
for i in range(n):
    model += (in_S[i] + in_T[i]) <= 1

# Constraint 2: Both S and T are non-empty
model += cp.sum(in_S) >= 1
model += cp.sum(in_T) >= 1

# Constraint 3: S and T have equal sums
sum_S = cp.sum([A[i] * in_S[i] for i in range(n)])
sum_T = cp.sum([A[i] * in_T[i] for i in range(n)])
model += sum_S == sum_T

# Symmetry breaking: prefer smaller indices in S
model += in_S[0] >= in_T[0]

# Step 4: Solve and verify
if model.solve():
    # Extract solution
    s_membership = in_S.value()
    t_membership = in_T.value()
    
    # Convert to integer lists for JSON output
    s_list = [int(x) for x in s_membership]
    t_list = [int(x) for x in t_membership]
    
    # Verification
    def verify_solution(s_list, t_list, A):
        # Check disjoint constraint
        for i in range(len(A)):
            if s_list[i] == 1 and t_list[i] == 1:
                return False, f"Element {i} is in both S and T"
        
        # Check non-empty constraints
        if sum(s_list) == 0 or sum(t_list) == 0:
            return False, "One of the subsets is empty"
        
        # Check equal sums
        sum_S = sum(A[i] for i in range(len(A)) if s_list[i] == 1)
        sum_T = sum(A[i] for i in range(len(A)) if t_list[i] == 1)
        
        if sum_S != sum_T:
            return False, f"Sums are not equal: S={sum_S}, T={sum_T}"
        
        return True, f"All constraints satisfied. S={sum_S}, T={sum_T}"
    
    valid, message = verify_solution(s_list, t_list, A)
    assert valid, f"Verification failed: {message}"
    
    # Step 5: Output solution
    solution = {
        "in_S": s_list,
        "in_T": t_list
    }
    
    print(json.dumps(solution))
    
else:
    print(json.dumps({"error": "No solution found"}))