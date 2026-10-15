# Word design: find num_words words of length n over {A, C, G, T}, each with exactly 4 symbols from {C, G},
# pairwise differing in at least 4 positions, and with x^R and y^C differing in at least 4 positions for all x, y in the set.
from pyscipopt import Model, quicksum

# letters are numbered 1 = A, 2 = C, 3 = G, 4 = T; the Watson-Crick complement maps v to 5 - v (A<->T, C<->G)
LETTERS = (1, 2, 3, 4)
GC_LETTERS = (2, 3)


def build(instance):
    n = instance["n"]
    num_words = instance["num_words"]
    model = Model()

    # b[k, i, v] = 1 if word k has letter v at position i (one-hot encoding of each letter)
    b = {(k, i, v): model.addVar(name=f"b_{k}_{i}_{v}", vtype="B")
         for k in range(num_words) for i in range(n) for v in LETTERS}
    for k in range(num_words):
        for i in range(n):
            # each position holds exactly one letter
            model.addCons(quicksum(b[k, i, v] for v in LETTERS) == 1)

    # each word has exactly 4 symbols from {C, G}
    for k in range(num_words):
        model.addCons(quicksum(b[k, i, v] for i in range(n) for v in GC_LETTERS) == 4)

    # e[k, l, i] = 1 is forced when words k and l carry the same letter at position i
    # (only the lower bound is needed, since the count of agreements is limited below)
    for k in range(num_words):
        for l in range(k + 1, num_words):
            agree = []
            for i in range(n):
                e = model.addVar(name=f"agree_{k}_{l}_{i}", vtype="B")
                for v in LETTERS:
                    model.addCons(e >= b[k, i, v] + b[l, i, v] - 1)
                agree.append(e)
            # distinct words differ in at least 4 positions, so at most n - 4 positions agree
            # ("each pair of distinct words in S differ in at least 4 positions")
            model.addCons(quicksum(agree) <= n - 4)

    # for every ordered pair (k, l), including k == l: the reverse of word k and the complement of word l
    # differ in at least 4 positions. f[k, l, i] = 1 is forced when x^R[i] equals y^C[i]
    for k in range(num_words):
        for l in range(num_words):
            same = []
            for i in range(n):
                f = model.addVar(name=f"rc_{k}_{l}_{i}", vtype="B")
                # x^R[i] = x[n - 1 - i]; y^C[i] = 5 - y[i]
                for v in LETTERS:
                    model.addCons(f >= b[k, n - 1 - i, v] + b[l, i, 5 - v] - 1)
                same.append(f)
            # x^R and y^C differ in at least 4 positions ("x^R and y^C differ in at least 4 positions")
            model.addCons(quicksum(same) <= n - 4)

    # the output gives each word as a list of letter codes 1..4
    words = [[quicksum(v * b[k, i, v] for v in LETTERS) for i in range(n)] for k in range(num_words)]
    return model, {"words": words}
