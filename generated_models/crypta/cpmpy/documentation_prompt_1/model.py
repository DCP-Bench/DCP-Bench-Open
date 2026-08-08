
import cpmpy as cp
import json

# Letters: A, B, C, D, E, F, G, H, I, J
letters = "ABCDEFGHIJ"
n_letters = len(letters)

# The cryptarithmetic addition:
#   B A I J J A J I I A H F C F E B B J E A
# + D H F G A B C D I D B I F F A G F E J E
# -----------------------------------------
# = G J E G A C D D H F A F J B F I H E E F

# We will model the addition column by column from right to left
# Each letter is a digit 0..9, all distinct

# Map letters to variables
vars_dict = {l: cp.intvar(0, 9, name=l) for l in letters}

# All letters distinct
model = cp.Model()
model += cp.AllDifferent(list(vars_dict.values()))

# Extract variables for convenience
A = vars_dict['A']
B = vars_dict['B']
C = vars_dict['C']
D = vars_dict['D']
E = vars_dict['E']
F = vars_dict['F']
G = vars_dict['G']
H = vars_dict['H']
I = vars_dict['I']
J = vars_dict['J']

# The addition has 21 digits on the left and 21 digits on the right
# Let's index digits from right to left (0-based)
# Left addend 1 digits (top):
# B A I J J A J I I A H F C F E B B J E A
# positions: 20 19 18 ... 0
# Let's write them in a list from right to left (pos 0 is rightmost)
top_digits_letters = [
    'A', 'E', 'J', 'B', 'B', 'E', 'F', 'C', 'F', 'H', 'A', 'I', 'I', 'J', 'A', 'J', 'J', 'I', 'A', 'B', 'B'
]
# Wait, the problem line is:
# B A I J J A J I I A H F C F E B B J E A
# Let's write carefully from left to right (pos 20 to 0):
# pos 20: B
# pos 19: A
# pos 18: I
# pos 17: J
# pos 16: J
# pos 15: A
# pos 14: J
# pos 13: I
# pos 12: I
# pos 11: A
# pos 10: H
# pos 9: F
# pos 8: C
# pos 7: F
# pos 6: E
# pos 5: B
# pos 4: B
# pos 3: J
# pos 2: E
# pos 1: A
# pos 0: (missing? The problem line has 21 letters, so pos 0 is A)
# Actually, the last letter is A at pos 0.

top_digits_letters = [
    'A', 'E', 'J', 'B', 'B', 'E', 'F', 'C', 'F', 'H', 'A', 'I', 'I', 'J', 'A', 'J', 'J', 'I', 'A', 'B', 'B'
]
# This is reversed from the original line, which is:
# B A I J J A J I I A H F C F E B B J E A
# So from left to right: pos 20 to pos 0
# So pos 0 is A (rightmost)
# So top_digits_letters reversed is:
top_digits_letters = list("BAIJJAJIIAHFCFEBBJEA")
# length is 20, but problem line has 21 letters, so let's count carefully:
# B A I J J A J I I A H F C F E B B J E A
# Count letters: 21 letters
# So top_digits_letters = ['B','A','I','J','J','A','J','I','I','A','H','F','C','F','E','B','B','J','E','A']
# That's 20 letters, missing one? Let's count again:
# B(1) A(2) I(3) J(4) J(5) A(6) J(7) I(8) I(9) A(10) H(11) F(12) C(13) F(14) E(15) B(16) B(17) J(18) E(19) A(20)
# Only 20 letters, but problem states 21 letters in the sum line.
# The problem line is:
# B A I J J A J I I A H F C F E B B J E A
# + D H F G A B C D I D B I F F A G F E J E
# -----------------------------------------
# = G J E G A C D D H F A F J B F I H E E F
# Let's count the letters in the first addend line carefully:
# B A I J J A J I I A H F C F E B B J E A
# Count: B(1), A(2), I(3), J(4), J(5), A(6), J(7), I(8), I(9), A(10), H(11), F(12), C(13), F(14), E(15), B(16), B(17), J(18), E(19), A(20)
# Only 20 letters, so the first addend has 20 digits.
# Second addend line:
# D H F G A B C D I D B I F F A G F E J E
# Count letters: D(1), H(2), F(3), G(4), A(5), B(6), C(7), D(8), I(9), D(10), B(11), I(12), F(13), F(14), A(15), G(16), F(17), E(18), J(19), E(20)
# 20 letters again.
# Result line:
# G J E G A C D D H F A F J B F I H E E F
# Count letters: G(1), J(2), E(3), G(4), A(5), C(6), D(7), D(8), H(9), F(10), A(11), F(12), J(13), B(14), F(15), I(16), H(17), E(18), E(19), F(20)
# 20 letters again.
# So all lines have 20 digits, not 21.

# So the problem statement has 20 digits per line.

# Let's write the digits from right to left (pos 0 is rightmost):

top_digits_letters = list("BAIJJAJIIAHFCFEBBJEA")
top_digits_letters = top_digits_letters[::-1]  # reverse to get right to left

bottom_digits_letters = list("DHFGABCDIDBIFFAGFEJE")
bottom_digits_letters = bottom_digits_letters[::-1]

result_digits_letters = list("GJEGACDDHFAFJBFIHEEF")
result_digits_letters = result_digits_letters[::-1]

length = 20

# We will add column by column with carry
carry = cp.intvar(0, 100, shape=length+1, name="carry")
model += (carry[0] == 0)

for i in range(length):
    top_digit = vars_dict[top_digits_letters[i]]
    bottom_digit = vars_dict[bottom_digits_letters[i]]
    result_digit = vars_dict[result_digits_letters[i]]
    # sum with carry
    model += (top_digit + bottom_digit + carry[i] == result_digit + 10 * carry[i+1])

# Leading digits cannot be zero
model += (vars_dict[top_digits_letters[-1]] != 0)
model += (vars_dict[bottom_digits_letters[-1]] != 0)
model += (vars_dict[result_digits_letters[-1]] != 0)

# Solve
if model.solve():
    solution = {l: int(vars_dict[l].value()) for l in letters}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
