
import cpmpy as cp
import json

# Letters: A, B, C, D, E, F, G, H, I, J
letters = "ABCDEFGHIJ"
n_letters = len(letters)

# Map letter to index
idx = {l: i for i, l in enumerate(letters)}

# The puzzle:
#   B A I J J A J I I A H F C F E B B J E A
# + D H F G A B C D I D B I F F A G F E J E
# -----------------------------------------
# = G J E G A C D D H F A F J B F I H E E F

# We want to represent each line as a list of letter indices, from left to right
top_line = [idx[l] for l in "BAIJJAJIIAHFCFEBBJEA"]
bot_line = [idx[l] for l in "DHFGABCDIDBIFFAGFEJE"]
res_line = [idx[l] for l in "GJEGACDDHFAFJBFIHEEF"]

length = len(top_line)  # 21 letters in each line

model = cp.Model()

# Variables for each letter digit 0..9
digits = cp.intvar(0, 9, shape=n_letters, name="digits")

# All letters must be distinct
model += cp.AllDifferent(digits)

# Leading letters cannot be zero:
# The first letter of top_line, bot_line, and res_line
model += digits[top_line[0]] != 0
model += digits[bot_line[0]] != 0
model += digits[res_line[0]] != 0

# The addition is digit-wise from right to left with carry
carry = cp.intvar(0, 2, shape=length, name="carry")  # carry[i] is carry into digit i (from right)
# carry[length-1] is the carry into the leftmost digit (most significant)
# carry[-1] will be zero by definition (no carry out from leftmost digit)
# We'll use carry[-1] = 0 for convenience.

# To handle that, let's create an array carry of length length+1 for convenience:
carry = cp.intvar(0, 2, shape=length+1, name="carry")
model += carry[length] == 0  # No carry out beyond the leftmost digit

# We process digits from right (index length-1) to left (index 0)
for i in reversed(range(length)):
    top_d = digits[top_line[i]]
    bot_d = digits[bot_line[i]]
    res_d = digits[res_line[i]]
    # Sum of top digit + bottom digit + carry from right == result digit + 10 * carry to left
    model += top_d + bot_d + carry[i+1] == res_d + 10 * carry[i]

if model.solve():
    solution = {letters[i]: int(digits[i].value()) for i in range(n_letters)}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
