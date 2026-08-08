# Import libraries
from cpmpy import *
import json

# Parameters
n = 8  # Number of words to find
word_length = 8  # Length of each word
alphabet = ['A', 'C', 'G', 'T']  # Possible symbols in words

# Decision Variables
# Represent words as integer variables (0=A, 1=C, 2=G, 3=T)
words = intvar(0, 3, shape=(n, word_length), name="words")

# Model
model = Model()

# Constraint 1: Each word has exactly 4 symbols from {C,G} (which are 1 and 2)
for i in range(n):
    model += sum((words[i] == 1) | (words[i] == 2)) == 4

# Constraint 2: Each pair of distinct words differ in at least 4 positions
for i in range(n):
    for j in range(i+1, n):
        # Count number of differing positions
        diff = sum(words[i,k] != words[j,k] for k in range(word_length))
        model += diff >= 4

# Constraint 3: For each pair x,y (including identical pairs), x^R and y^C differ in at least 4 positions
for i in range(n):
    for j in range(n):
        # Compute x^R (reverse) and y^C (complement)
        # y^C: A<->T (0<->3), C<->G (1<->2)
        diff_count = 0
        for k in range(word_length):
            x_rev = words[i, word_length-1 - k]  # x^R
            y_val = words[j,k]  # original y value
            # Calculate complement of y
            y_comp = (3 - y_val) if (y_val in [0,3]) else (3 - y_val)
            diff_count += (x_rev != y_comp)
        model += diff_count >= 4

# Solve
model.solve()

# Output solution as integers
if model.solve():
    solution = {"words": words.value().tolist()}
    print(json.dumps(solution))
else:
    print(json.dumps({"words": []}))
# End of CPMPy script