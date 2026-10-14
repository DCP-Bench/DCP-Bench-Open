"""Word design: find a set of DNA words of length n that are far apart from each other.

Words use the letters A, C, G, T (coded 1, 2, 3, 4). Each word has exactly 4 letters from
{C, G}. Two different words differ in at least 4 positions. For any two words x and y
(possibly the same word), the reverse of x and the Watson-Crick complement of y differ in
at least 4 positions, where the complement swaps A with T and C with G.
"""
from itertools import combinations

from docplex.mp.model import Model

LETTERS = (1, 2, 3, 4)  # A, C, G, T: a fixed part of the problem
STRONG = (2, 3)         # the letters C and G
MIN_DISTANCE = 4        # positions in which two words must differ: a fixed part of the problem
STRONG_PER_WORD = 4     # letters from {C, G} in every word: a fixed part of the problem


def build(instance):
    n = instance["n"]              # length of each word
    num_words = instance["num_words"]

    positions = range(n)
    words = range(num_words)

    model = Model("word_design")
    # The distance rules below are quadratic constraints over binaries, which are not
    # convex. CPLEX refuses such a constraint unless it is told to search for a global optimum.
    model.parameters.optimalitytarget = 3

    # letter[x, j, c] is 1 when the j-th letter of word x is c.
    letter = model.binary_var_cube(words, positions, LETTERS, name="letter")

    # Every position of every word holds exactly one letter.
    for x in words:
        for j in positions:
            model.add_constraint(model.sum(letter[x, j, c] for c in LETTERS) == 1)

    # Each word has exactly 4 letters from {C, G}.
    for x in words:
        model.add_constraint(
            model.sum(letter[x, j, c] for j in positions for c in STRONG) == STRONG_PER_WORD)

    # Two different words differ in at least 4 positions, i.e. they agree in at most n - 4.
    # The agreements are counted as products of the two words' letter indicators.
    for x, y in combinations(words, 2):
        agreements = model.sum(letter[x, j, c] * letter[y, j, c]
                               for j in positions for c in LETTERS)
        model.add_constraint(agreements <= n - MIN_DISTANCE)

    # For every pair of words x and y (also x with itself), the reverse of x and the
    # complement of y differ in at least 4 positions. Position j compares the letter of x at
    # n - 1 - j with the complement of the letter of y at j; the complement of c is 5 - c.
    # The pair (y, x) gives the same rule as (x, y), so each unordered pair is stated once.
    for x in words:
        for y in range(x, num_words):
            agreements = model.sum(letter[x, n - 1 - j, c] * letter[y, j, 5 - c]
                                   for j in positions for c in LETTERS)
            model.add_constraint(agreements <= n - MIN_DISTANCE)

    # The declared output: the letters of every word.
    return model, {"words": [[model.sum(c * letter[x, j, c] for c in LETTERS) for j in positions]
                             for x in words]}
