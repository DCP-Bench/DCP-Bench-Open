# Word design for DNA computing: find a set of words over the alphabet
# {A, C, G, T} with exactly four C/G letters each, any two distinct words
# differing in at least four positions, and every word's reverse differing
# from every word's Watson-Crick complement in at least four positions.
from hermax.model import Model

# Constants fixed by the problem statement, not instance fields.
A, C, G, T = 1, 2, 3, 4  # letters are coded 1..4
CG_PER_WORD = 4  # each word has this many letters from {C, G}
MIN_DISTANCE = 4  # the required number of differing positions


def build(instance):
    n = instance["n"]  # length of each word
    num_words = instance["num_words"]  # size of the set

    m = Model()
    # words[i][j] = the j-th letter of word i
    words = m.int_matrix("words", num_words, n, A, T)

    # Each word has exactly four letters from {C, G}. strong[i][j] says that
    # letter j of word i is C or G (at least C, below T), stated both ways.
    for i in range(num_words):
        strong = m.bool_vector(f"strong_{i}", n)
        for j in range(n):
            m &= (~strong[j] | (words[i][j] >= C))
            m &= (~strong[j] | ~(words[i][j] >= T))
            m &= (strong[j] | ~(words[i][j] >= C) | (words[i][j] >= T))
        m &= (sum(strong[j] for j in range(n)) == CG_PER_WORD)

    # Two distinct words differ in at least four positions. differ[j] is only
    # allowed to be true when the letters at position j really differ; it is
    # then counted, so the count is a lower bound on the true distance and the
    # constraint holds exactly when the distance is large enough.
    for x in range(num_words):
        for y in range(x + 1, num_words):
            differ = m.bool_vector(f"differ_{x}_{y}", n)
            for j in range(n):
                for letter in range(A, T + 1):
                    m &= (~differ[j] | ~(words[x][j] == letter) | ~(words[y][j] == letter))
            m &= (sum(differ[j] for j in range(n)) >= MIN_DISTANCE)

    # The reverse of word x differs from the Watson-Crick complement of word y
    # (A<->T, C<->G, i.e. letter l becomes 5 - l) in at least four positions;
    # this holds for every pair, a word with itself included. The requirement
    # for the pair (y, x) is the same constraint as for (x, y) read from the
    # other end, so each unordered pair is posted once.
    for x in range(num_words):
        for y in range(x, num_words):
            differ = m.bool_vector(f"reverse_{x}_{y}", n)
            for j in range(n):
                for letter in range(A, T + 1):
                    # position j of the reversed x is letter n-1-j of x; position j
                    # of the complemented y holds 5 - letter exactly when y has `letter`
                    m &= (~differ[j] | ~(words[x][n - 1 - j] == letter)
                          | ~(words[y][j] == A + T - letter))
            m &= (sum(differ[j] for j in range(n)) >= MIN_DISTANCE)

    return m, {"words": words}
