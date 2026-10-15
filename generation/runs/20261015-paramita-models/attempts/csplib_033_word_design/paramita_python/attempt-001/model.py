# Word design over the alphabet {A, C, G, T} (CSPLib 033).
#
# Find num_words words of length n such that:
#   - each word has exactly 4 symbols from {C, G};
#   - each pair of distinct words differs in at least 4 positions;
#   - for each pair x, y (x = y allowed), the reverse of x and the Watson-Crick
#     complement of y differ in at least 4 positions.
#
# Encoding: one-hot per position. x[w][p][l] = 1 when word w has letter l at
# position p, with the letters A=0, C=1, G=2, T=3. The Watson-Crick complement
# swaps A and T and swaps C and G, which is l -> 3 - l. Each "differ in at least
# 4 positions" is a Bool per position that may be true only where the letters
# differ, and a cardinality constraint over those Bools.

from paramita.modelling import Bool, If

A, C, G, T = 0, 1, 2, 3
LETTERS = (A, C, G, T)


def build(instance):
    n, num_words = instance["n"], instance["num_words"]

    # x[w][p][l] = 1 if word w has letter l at position p
    x = [[{l: Bool(f"x_{w}_{p}_{l}") for l in LETTERS} for p in range(n)]
         for w in range(num_words)]

    cons = []

    # every position of every word holds exactly one letter
    for w in range(num_words):
        for p in range(n):
            cons.append(sum(x[w][p][l] for l in LETTERS) == 1)

    # each word has exactly 4 symbols from {C, G}
    for w in range(num_words):
        cons.append(sum(x[w][p][C] + x[w][p][G] for p in range(n)) == 4)

    def differ_in_four(tag, first, second):
        # first[p] and second[p] are the letters compared at position p, given as
        # one-hot dicts. The Bool d[p] may be true only where the letters differ;
        # at least 4 such positions are required.
        d = [Bool(f"d_{tag}_{p}") for p in range(n)]
        for p in range(n):
            for l in LETTERS:
                cons.append(If(d[p], ~(first[p][l] & second[p][l])))
        cons.append(sum(d) >= 4)

    # distinct words differ in at least 4 positions (each unordered pair once)
    for w1 in range(num_words):
        for w2 in range(w1 + 1, num_words):
            differ_in_four(f"ham_{w1}_{w2}", x[w1], x[w2])

    # reverse of x and Watson-Crick complement of y differ in at least 4 positions,
    # for every ordered pair (x, y), including x = y. Position p of x^R is
    # position n-1-p of x; position p of y^C is the complement of letter p of y.
    for w1 in range(num_words):
        for w2 in range(num_words):
            rev_first = [x[w1][n - 1 - p] for p in range(n)]
            comp_second = [
                {l: x[w2][p][3 - l] for l in LETTERS} for p in range(n)
            ]
            differ_in_four(f"rc_{w1}_{w2}", rev_first, comp_second)

    # output: word w as a list of n letter codes, 1 = A, 2 = C, 3 = G, 4 = T
    words = [
        [sum((l + 1) * x[w][p][l] for l in LETTERS) for p in range(n)]
        for w in range(num_words)
    ]
    return cons, {"words": words}
