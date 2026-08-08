# Import libraries
from cpmpy import *
import json

# Parameters
n = 8  # Number of words to find
word_length = 8  # Length of each word
alphabet = ["A", "C", "G", "T"]  # Alphabet
alphabet_map = {"A": 0, "C": 1, "G": 2, "T": 3}  # Map for encoding
alphabet_size = len(alphabet)  # Size of the alphabet

# Decision variables
# Each word is a sequence of symbols from the alphabet
words = intvar(0, alphabet_size - 1, shape=(n, word_length), name="words")

# Model
model = Model()

# Constraint 1: Each word has exactly 4 symbols from {C, G}
for i in range(n):
    model += [sum((words[i] == 1) | (words[i] == 2)) == 4]

# Constraint 2: Each pair of distinct words differ in at least 4 positions
for i in range(n):
    for j in range(i + 1, n):
        model += [sum(words[i] != words[j]) >= 4]

# Constraint 3: For each pair of words x and y, x^R and y^C differ in at least 4 positions
for i in range(n):
    for j in range(n):
        # x^R is the reverse of the i-th word
        x_rev = words[i, ::-1]
        # y^C is the Watson-Crick complement of the j-th word
        y_comp = [3 if words[j, k] == 0 else 0 if words[j, k] == 3 else words[j, k] for k in range(word_length)]
        y_comp = cpm_array(y_comp)
        model += [sum(x_rev != y_comp) >= 4]

# Solve the model
model.solve()

# Print the solution
solution = {"words": words.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script