
import cpmpy as cp
import json

# Data
n = 8  # Number of words to find
length = 8
alphabet = ['A', 'C', 'G', 'T']
# Map letters to integers for modeling: A=0, C=1, G=2, T=3
char_map = {'A':0, 'C':1, 'G':2, 'T':3}
rev_char_map = {v:k for k,v in char_map.items()}

# Complement map for Watson-Crick complement:
# A <-> T, C <-> G
# Using integers: 0<->3, 1<->2
complement = [3, 2, 1, 0]

# Model definition
model = cp.Model()

# Decision Variables
# words: n words of length 8, values in [0..3]
words = cp.intvar(0, 3, shape=(n, length), name="words")

# Constraints

# 1) Each word has exactly 4 symbols from {C,G} i.e. values 1 or 2
for i in range(n):
    model += (cp.Count(words[i], 1) + cp.Count(words[i], 2) == 4)

# 2) Each pair of distinct words differ in at least 4 positions (Hamming distance >=4)
for i in range(n):
    for j in range(i+1, n):
        diff_positions = [words[i,k] != words[j,k] for k in range(length)]
        model += (cp.sum(diff_positions) >= 4)

# Complement variables for words
comp_words = cp.intvar(0,3, shape=(n,length), name="comp_words")
for j in range(n):
    for k in range(length):
        model += cp.Element(complement, words[j,k]) == comp_words[j,k]

# 3) For each pair x,y (including x=y), x^R and y^C differ in at least 4 positions
for i in range(n):
    for j in range(n):
        diffs = []
        for k in range(length):
            diffs.append(words[i,length-1-k] != comp_words[j,k])
        model += (cp.sum(diffs) >= 4)

# Solve and print
if model.solve():
    solution = {'words': words.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
