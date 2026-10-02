# Word design for DNA computing: find a set of DNA words of equal length with
# four C/G symbols each, pairwise far apart, and far from the reverse complements
# of all words (including their own).
import z3

# Constants of the problem statement (not of the instance), mirrored from the reference.
A, T = 1, 4                 # letters are coded 1 = A, 2 = C, 3 = G, 4 = T
C, G = 2, 3
GC_COUNT = 4                # every word has exactly 4 symbols from {C, G}
MIN_DISTANCE = 4            # required number of differing positions


def build(instance):
    n = instance["n"]                  # length of each word
    num_words = instance["num_words"]  # number of words to find

    # words[i][j] is the j-th letter of the i-th word.
    words = [[z3.Int(f"words_{i}_{j}") for j in range(n)] for i in range(num_words)]

    solver = z3.Solver()

    for word in words:
        for letter in word:
            solver.add(letter >= A, letter <= T)

    # Each word has exactly 4 symbols from {C, G}.
    for word in words:
        solver.add(z3.Sum([z3.If(z3.Or(letter == C, letter == G), 1, 0)
                           for letter in word]) == GC_COUNT)

    # Each pair of distinct words differs in at least 4 positions.
    for i in range(num_words):
        for k in range(i + 1, num_words):
            solver.add(z3.Sum([z3.If(words[i][j] != words[k][j], 1, 0)
                               for j in range(n)]) >= MIN_DISTANCE)

    # For every pair of words x and y (also x = y), the reverse of x and the
    # Watson-Crick complement of y (A<->T, C<->G, i.e. letter -> 5 - letter)
    # differ in at least 4 positions.
    for x in words:
        for y in words:
            solver.add(z3.Sum([z3.If(x[n - 1 - j] != 5 - y[j], 1, 0)
                               for j in range(n)]) >= MIN_DISTANCE)

    return solver, {"words": words}
