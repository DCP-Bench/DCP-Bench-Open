
import cpmpy as cp
import json

# Data
n = 8  # Number of words to find
L = 8  # length of each word
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# words[i][p] in {1(A),2(C),3(G),4(T)}
words = cp.intvar(1, 4, shape=(n, L), name="words")

# Constraints

# 1) Each word has exactly 4 symbols from {C=2, G=3}
for i in range(n):
    model += cp.Among([words[i, p] for p in range(L)], [2, 3]) == 4

# 2) Pairwise Hamming distance between distinct words >= 4
for i in range(n):
    for j in range(i + 1, n):
        model += cp.sum([words[i, p] != words[j, p] for p in range(L)]) >= 4

# 3) For any pair x (i) and y (j) (including i==j), x^R and y^C differ in at least 4 positions.
# Complement mapping: c(v) = 5 - v  (1<->4, 2<->3)
for i in range(n):
    for j in range(n):
        model += cp.sum([words[i, L - 1 - p] != (5 - words[j, p]) for p in range(L)]) >= 4

# Symmetry breaking: enforce lexicographic non-decreasing order of rows
model += cp.LexChainLessEq([words[i] for i in range(n)])

# Solve and print
if model.solve():
    solution = {'words': words.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
