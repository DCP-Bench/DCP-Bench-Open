# Word design for DNA: find num_words words of length n over the letters
# A, C, G, T (numbered 1..4) such that every word has exactly four letters from
# {C, G}, any two different words differ in at least four positions, and for
# any two words x and y (possibly the same) the reverse of x differs from the
# Watson-Crick complement of y in at least four positions.
import cpmpy as cp

A, C, G, T = 1, 2, 3, 4  # letters as numbers; the complement of letter v is 5 - v (problem constant)
GC_LETTERS = 4           # letters from {C, G} in every word (fixed by the problem statement)
MIN_DIFFERENCES = 4      # positions in which two words must differ (fixed by the problem statement)


def build(instance):
    n = instance["n"]  # length of each word
    num_words = instance["num_words"]

    # words[i, j] is the j-th letter of word i
    words = cp.intvar(A, T, shape=(num_words, n), name="words")

    model = cp.Model()

    # Each word has exactly four letters from {C, G}.
    for w in words:
        model += cp.sum((w == C) | (w == G)) == GC_LETTERS

    # Any two different words differ in at least four positions.
    for i in range(num_words):
        for k in range(i + 1, num_words):
            model += cp.sum(words[i] != words[k]) >= MIN_DIFFERENCES

    # For every ordered pair of words (x, y), including x = y, the reverse of x differs from the
    # Watson-Crick complement of y (each letter v replaced by 5 - v) in at least four positions.
    for y in words:
        y_complement = 5 - y
        for x in words:
            x_reversed = x[::-1]
            model += cp.sum(x_reversed != y_complement) >= MIN_DIFFERENCES

    return model, {"words": words}
