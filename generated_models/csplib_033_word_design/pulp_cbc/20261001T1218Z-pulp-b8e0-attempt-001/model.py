"""Word design for DNA computing: find num_words strings of length n over the
alphabet {A, C, G, T} that can be used together without unwanted hybridisation.

The letters are coded 1 for A, 2 for C, 3 for G and 4 for T.
  - Each word has exactly 4 letters from {C, G}.
  - Any two different words differ in at least 4 positions.
  - For any two words x and y (possibly the same word), the reverse of x and the
    Watson-Crick complement of y (A<->T, C<->G, i.e. letter l becomes 5 - l)
    differ in at least 4 positions.
"""
import pulp

A, C, G, T = 1, 2, 3, 4
LETTERS = (A, C, G, T)
# The three thresholds below are the problem's own constants, not instance data:
# the reference fixes them at 4 for every instance.
CG_COUNT = 4
MIN_DIFFERENCE = 4


def build(instance):
    n = instance["n"]                  # length of each word
    num_words = instance["num_words"]  # number of words to find

    problem = pulp.LpProblem("word_design", pulp.LpMinimize)

    # has[i][j][l] = 1 if letter j of word i is the letter l
    has = [[{l: pulp.LpVariable(f"has_{i}_{j}_{l}", cat="Binary") for l in LETTERS}
            for j in range(n)] for i in range(num_words)]

    # words[i][j] = the letter at position j of word i (declared output), a bounded
    # integer tied to the 0/1 variables by equality
    words = [[pulp.LpVariable(f"words_{i}_{j}", A, T, cat="Integer") for j in range(n)]
             for i in range(num_words)]

    # every position of every word holds exactly one letter, and words reads it back
    for i in range(num_words):
        for j in range(n):
            problem += pulp.lpSum(has[i][j].values()) == 1
            problem += words[i][j] == pulp.lpSum(l * has[i][j][l] for l in LETTERS)

    # each word has exactly 4 letters from {C, G}
    for i in range(num_words):
        problem += pulp.lpSum(has[i][j][C] + has[i][j][G] for j in range(n)) == CG_COUNT

    # each pair of distinct words differ in at least 4 positions: same[j] is forced to
    # 1 when the two words hold the same letter at position j, so the number of equal
    # positions is at most n - 4. One lower-bound row per letter suffices because
    # each position holds exactly one letter.
    for x in range(num_words):
        for y in range(x + 1, num_words):
            same = [pulp.LpVariable(f"same_{x}_{y}_{j}", 0, 1) for j in range(n)]
            for j in range(n):
                for l in LETTERS:
                    problem += same[j] >= has[x][j][l] + has[y][j][l] - 1
            problem += pulp.lpSum(same) <= n - MIN_DIFFERENCE

    # for every ordered pair of words (x, y), including x = y: reversed x and the
    # complement of y differ in at least 4 positions. Position j of reversed x is
    # letter n-1-j of x; the complement of letter l is 5 - l, so the two agree at
    # position j when letter n-1-j of x is l and letter j of y is 5 - l.
    for x in range(num_words):
        for y in range(num_words):
            agree = [pulp.LpVariable(f"agree_{x}_{y}_{j}", 0, 1) for j in range(n)]
            for j in range(n):
                for l in LETTERS:
                    problem += agree[j] >= has[x][n - 1 - j][l] + has[y][j][5 - l] - 1
            problem += pulp.lpSum(agree) <= n - MIN_DIFFERENCE

    return problem, {"words": words}
