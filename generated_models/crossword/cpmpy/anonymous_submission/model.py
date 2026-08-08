from cpmpy import *
import json

# Decision Variables
E = intvar(0, 14, shape=8, name="E")  # Selected words for each number (1-8)

# Word lengths (index corresponds to word order: HOSES=0=5 letters, ..., TIE=14=3 letters)
word_lengths = [5,5,5,5,5,4,4,4,4,4,3,3,3,3,3]

# Model
model = Model()

# Constraint: All selected words must be distinct
model += AllDifferent(E)

# Word assignments to numbers with correct lengths using array indexing
model += word_lengths[E[0]] == 5  # Word 1
model += word_lengths[E[1]] == 5  # Word 2
model += word_lengths[E[2]] == 4  # Word 3
model += word_lengths[E[3]] == 4  # Word 4
model += word_lengths[E[4]] == 4  # Word 5
model += word_lengths[E[5]] == 4  # Word 6
model += word_lengths[E[6]] == 3  # Word 7
model += word_lengths[E[7]] == 3  # Word 8

# Solve
model.solve()

# Print solution
solution = {"E": E.value().tolist()}
print(json.dumps(solution))