
import cpmpy as cp
import json

# Data (optional)
n = 8  # Number of words to find
L = 8  # Length of each word
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# words[i][k] in {1:A, 2:C, 3:G, 4:T}
words = cp.intvar(1, 4, shape=(n, L), name="words")

# Constraints

# 1) Each word has exactly 4 symbols from {C,G} i.e., values {2,3}
for i in range(n):
    model += (cp.Among([words[i, k] for k in range(L)], [2, 3]) == 4)

# 2) Each pair of distinct words differ in at least 4 positions (Hamming distance >= 4)
for i in range(n):
    for j in range(i + 1, n):
        model += (cp.sum([words[i, k] != words[j, k] for k in range(L)]) >= 4)

# 3) For all pairs (x, y), reverse(x) and complement(y) differ in at least 4 positions
# complement mapping: 1<->4 (A<->T), 2<->3 (C<->G) => comp(v) = 5 - v
for i in range(n):
    for j in range(n):
        model += (cp.sum([words[i, L - 1 - k] != (5 - words[j, k]) for k in range(L)]) >= 4)

# Symmetry breaking to help the solver
# - Enforce strict lexicographic ordering of the words
model += cp.LexChainLess(words)
# - Fix the first symbol of the first word to 'A' to break global symmetries
model += (words[0, 0] == 1)

# Objective (optional)
# No objective; we only need a feasible set of n words

# Solve and print
if model.solve():
    solution = {'words': words.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
