# Word design: find a set of DNA words (A, C, G, T) of equal length such that each
# word has four C/G letters, any two distinct words differ in at least four
# positions, and any reversed word differs from any complemented word in at
# least four positions.
from pychoco.model import Model

# Letters are coded as in the problem statement: 1 = A, 2 = C, 3 = G, 4 = T.
A, C, G, T = 1, 2, 3, 4
# Problem constants (fixed by the problem statement, not by the instance):
CG_PER_WORD = 4  # every word has exactly four letters from {C, G}
MIN_DIFFERENCES = 4  # minimum number of differing positions in each comparison


def build(instance):
    n = instance["n"]  # length of each word
    num_words = instance["num_words"]  # number of words to find

    model = Model()

    # words[i][j] = the j-th letter of the i-th word
    words = [[model.intvar(A, T, name=f"words_{i}_{j}") for j in range(n)] for i in range(num_words)]

    # each word has exactly four letters from {C, G}
    for word in words:
        model.among(model.intvar(CG_PER_WORD, CG_PER_WORD), word, [C, G]).post()

    # each pair of distinct words differs in at least four positions
    for i in range(num_words):
        for k in range(i + 1, num_words):
            differs = [model.arithm(words[i][j], "!=", words[k][j]).reify() for j in range(n)]
            model.sum(differs, ">=", MIN_DIFFERENCES).post()

    # for every pair of words x and y (also x = y), the reverse of x and the
    # Watson-Crick complement of y (A<->T, C<->G, i.e. letter 5 - y) differ in at
    # least four positions: position j compares x[n-1-j] with 5 - y[j],
    # which differ exactly when x[n-1-j] + y[j] != 5
    for x in words:
        for y in words:
            differs = [model.arithm(x[n - 1 - j], "+", y[j], "!=", 5).reify() for j in range(n)]
            model.sum(differs, ">=", MIN_DIFFERENCES).post()

    return model, {"words": words}
