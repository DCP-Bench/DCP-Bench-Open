import cpmpy as cp
import json

# Send More Money Cryptarithmetic Puzzle
# SEND + MORE = MONEY
# Each letter represents a unique digit 0-9
# Leading letters (S, M) cannot be 0

# Create model
model = cp.Model()

# Decision variables: each letter is a digit 0-9
s = cp.intvar(0, 9, name="s")
e = cp.intvar(0, 9, name="e") 
n = cp.intvar(0, 9, name="n")
d = cp.intvar(0, 9, name="d")
m = cp.intvar(0, 9, name="m")
o = cp.intvar(0, 9, name="o")
r = cp.intvar(0, 9, name="r")
y = cp.intvar(0, 9, name="y")

# Constraints
letters = [s, e, n, d, m, o, r, y]

# All letters must represent different digits
model += cp.AllDifferent(letters)

# Leading digits cannot be zero
model += s != 0  # SEND cannot start with 0
model += m != 0  # MORE and MONEY cannot start with 0

# Arithmetic constraint: SEND + MORE = MONEY
send = 1000*s + 100*e + 10*n + d
more = 1000*m + 100*o + 10*r + e
money = 10000*m + 1000*o + 100*n + 10*e + y

model += send + more == money

# Solve the model
if model.solve():
    # Extract solution
    solution = {
        "s": s.value(),
        "e": e.value(),
        "n": n.value(),
        "d": d.value(),
        "m": m.value(),
        "o": o.value(),
        "r": r.value(),
        "y": y.value()
    }
    
    # Verification
    def verify_solution(sol):
        # Check all values are digits 0-9
        for key, value in sol.items():
            if not isinstance(value, int) or value < 0 or value > 9:
                return False
        
        # Check all digits are unique
        values = list(sol.values())
        if len(set(values)) != len(values):
            return False
        
        # Check leading digit constraints
        if sol["s"] == 0 or sol["m"] == 0:
            return False
        
        # Verify arithmetic: SEND + MORE = MONEY
        send_val = 1000*sol["s"] + 100*sol["e"] + 10*sol["n"] + sol["d"]
        more_val = 1000*sol["m"] + 100*sol["o"] + 10*sol["r"] + sol["e"]
        money_val = 10000*sol["m"] + 1000*sol["o"] + 100*sol["n"] + 10*sol["e"] + sol["y"]
        
        return send_val + more_val == money_val
    
    assert verify_solution(solution), "Solution verification failed!"
    
    # Output in required JSON format
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))