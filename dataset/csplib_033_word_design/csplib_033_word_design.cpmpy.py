#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob033_word_design.py
# Source description: https://www.csplib.org/Problems/prob033/

# Data
n = 8  # Length of each word
num_words = 12  # Number of words to find
# End of data

# Import libraries
import json
from cpmpy import *
from cpmpy.expressions.utils import all_pairs

def word_design(num_words=8, n=8):
    A, C, G, T = 1, 2, 3, 4

    # words[i,j] is the j'th letter of the i'th word
    words = intvar(A, T, shape=(num_words, n), name="words")

    model = Model()

    # 4 symbols from {C,G}
    for w in words:
        model += sum((w == C) | (w == G)) == 4

    # Each pair of distinct words differ in at least 4 positions
    for x, y in all_pairs(words):
        model += (sum(x != y) >= 4)

    # Each pair of words x and y (where x and y may be identical)
    # are such that x^R and y^C differ in at least 4 positions
    for y in words:
        y_c = 5 - y  # Watson-Crick complement
        for x in words:
            x_r = x[::-1]  # reversed x
            model += sum(x_r != y_c) >= 4

    return model, (words,)

# Example usage
model, (words,) = word_design(num_words=num_words, n=n)
model.solve()

# Print
solution = {"words": words.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script

