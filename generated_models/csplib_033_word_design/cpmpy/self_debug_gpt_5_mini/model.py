
import cpmpy as cp
import json

# Data
n = 8  # Number of words to find
L = 8  # length of each word
# Alphabet encoding: 1=A, 2=C, 3=G, 4=T

# Model definition
model = cp.Model()

# Decision Variables: n words of length L, values in 1..4
words = cp.intvar(1, 4, shape=(n, L), name="words")

# Constraints

# 1) Each word has exactly 4 symbols from {C,G} i.e. values 2 or 3
for i in range(n):
    model += cp.sum([ (words[i, k] == 2) | (words[i, k] == 3) for k in range(L) ]) == 4

# 2) Each pair of distinct words differ in at least 4 positions (Hamming distance >= 4)
for i in range(n):
    for j in range(i+1, n):
        model += cp.sum([ words[i, k] != words[j, k] for k in range(L) ]) >= 4

# 3) For each pair x (i) and y (j) (including i == j), x^R and y^C differ in at least 4 positions.
# reverse of x: words[i, L-1-k]; complement of y: 5 - words[j, k]
for i in range(n):
    for j in range(n):
        model += cp.sum([ words[i, L-1-k] != (5 - words[j, k]) for k in range(L) ]) >= 4

# Symmetry breaking: order the words lexicographically non-decreasing to reduce search space
model += cp.LexChainLessEq([words[i] for i in range(n)])

# Solve and print
if model.solve():
    solution = {'words': words.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
