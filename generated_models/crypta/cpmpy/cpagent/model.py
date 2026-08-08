import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# Cryptarithmetic puzzle: B A I J J A J I I A H F C F E B B J E A
#                       + D H F G A B C D I D B I F F A G F E J E
#                       = G J E G A C D D H F A F J B F I H E E F
# All letters A-J must be distinct digits 0-9

line1 = "BAIJJAJIIAHFCFEBBJEA"
line2 = "DHFGABCDIDBIFFAGFEJE"
result = "GJEGACDDHFAFJBFIHEEF"

# Step 2: Model with CPMpy
letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
digit_vars = {}
for letter in letters:
    digit_vars[letter] = cp.intvar(0, 9, name=letter)

model = cp.Model()

# All letters must have different digits
model += cp.AllDifferent([digit_vars[letter] for letter in letters])

# Model the addition with carries
n_digits = len(line1)
carry = cp.intvar(0, 1, shape=n_digits+1, name="carry")
model += carry[n_digits] == 0  # No carry into the leftmost position

# Add constraints for each digit position (right to left)
for i in range(n_digits-1, -1, -1):
    l1_digit = digit_vars[line1[i]]
    l2_digit = digit_vars[line2[i]]
    res_digit = digit_vars[result[i]]
    
    # The equation for position i:
    # l1_digit + l2_digit + carry[i+1] = res_digit + 10 * carry[i]
    model += l1_digit + l2_digit + carry[i+1] == res_digit + 10 * carry[i]

# Step 3: Solve and verify
if model.solve():
    # Extract the solution
    solution = {}
    for letter in letters:
        solution[letter] = int(digit_vars[letter].value())
    
    # Verification - check the arithmetic independently
    def verify_solution(sol):
        def string_to_number(s):
            return int(''.join(str(sol[c]) for c in s))
        
        num1 = string_to_number(line1)
        num2 = string_to_number(line2)
        expected_result = string_to_number(result)
        actual_sum = num1 + num2
        
        # Check arithmetic correctness
        arithmetic_correct = actual_sum == expected_result
        
        # Check all digits are different
        digits_used = list(sol.values())
        all_different = len(set(digits_used)) == len(digits_used)
        
        return arithmetic_correct and all_different
    
    assert verify_solution(solution), "Solution verification failed!"
    
    # Step 4: Output in required JSON format
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))