
import cpmpy as cp
import json

# Define letters and their variables
letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
var_dict = {letter: cp.intvar(0, 9, name=letter) for letter in letters}

# Carry variables for each digit position (0 to 19)
carry_out = cp.intvar(0, 1, shape=20, name="carry_out")

# Reversed digits for each addend and sum
num1_letters = [
    'B', 'A', 'I', 'J', 'J', 'A', 'J', 'I', 'I', 'A', 'H', 'F', 'C', 'F', 'E', 'B', 'B', 'J', 'E', 'A'
]
reversed_num1 = num1_letters[::-1]

num2_letters = [
    'D', 'H', 'F', 'G', 'A', 'B', 'C', 'D', 'I', 'D', 'B', 'I', 'F', 'F', 'A', 'G', 'F', 'E', 'J', 'E'
]
reversed_num2 = num2_letters[::-1]

sum_letters = [
    'G', 'J', 'E', 'G', 'A', 'C', 'D', 'D', 'H', 'F', 'A', 'F', 'J', 'B', 'F', 'I', 'H', 'E', 'E', 'F'
]
reversed_sum = sum_letters[::-1]

# Initialize model
model = cp.Model()

# All letters must be distinct
model += cp.AllDifferent(var_dict.values())

# Leading digits cannot be zero
model += (var_dict['B'] != 0)
model += (var_dict['D'] != 0)
model += (var_dict['G'] != 0)

# Final carry must be zero
model += (carry_out[19] == 0)

# Add constraints for each digit position
for i in range(20):
    digit1 = var_dict[reversed_num1[i]]
    digit2 = var_dict[reversed_num2[i]]
    sum_d = var_dict[reversed_sum[i]]
    
    if i == 0:
        lhs = digit1 + digit2
    else:
        lhs = digit1 + digit2 + carry_out[i-1]
    
    model += (lhs == sum_d + 10 * carry_out[i])

# Solve and print solution
if model.solve():
    solution = {letter: int(var.value()) for letter, var in var_dict.items()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
