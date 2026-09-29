# Word design for DNA: find num_words words of length n over the letters
# A, C, G, T (numbered 1..4) such that every word has exactly four letters from
# {C, G}, any two different words differ in at least four positions, and for
# any two words x and y (possibly the same) the reverse of x differs from the
# Watson-Crick complement of y in at least four positions.
from ortools.sat.python import cp_model

A, C, G, T = 1, 2, 3, 4  # the letters as numbers; the complement of letter v is 5 - v
MIN_DIFFERENCES = 4  # positions in which two words must differ
GC_LETTERS = 4  # letters from {C, G} in every word


def build(instance):
    n = instance["n"]  # length of each word
    num_words = instance["num_words"]

    model = cp_model.CpModel()

    # words[i][j] = the j-th letter of word i
    words = [[model.new_int_var(A, T, f"words_{i}_{j}") for j in range(n)] for i in range(num_words)]

    # each word has exactly four letters from {C, G}
    for i in range(num_words):
        gc = []
        for j in range(n):
            is_gc = model.new_bool_var(f"gc_{i}_{j}")
            model.add_allowed_assignments([words[i][j], is_gc], [(A, 0), (C, 1), (G, 1), (T, 0)])
            gc.append(is_gc)
        model.add(sum(gc) == GC_LETTERS)

    # two different words differ in at least four positions
    for x in range(num_words):
        for y in range(x + 1, num_words):
            differ = []
            for j in range(n):
                d = model.new_bool_var(f"differ_{x}_{y}_{j}")
                model.add(words[x][j] != words[y][j]).only_enforce_if(d)
                model.add(words[x][j] == words[y][j]).only_enforce_if(d.negated())
                differ.append(d)
            model.add(sum(differ) >= MIN_DIFFERENCES)

    # the reverse of x differs from the complement of y in at least four positions,
    # for every ordered pair (x, y), including x = y
    for x in range(num_words):
        for y in range(num_words):
            differ = []
            for j in range(n):
                d = model.new_bool_var(f"rc_differ_{x}_{y}_{j}")
                # position j of reversed x is letter n-1-j of x; the complement of y[j] is 5 - y[j]
                model.add(words[x][n - 1 - j] + words[y][j] != 5).only_enforce_if(d)
                model.add(words[x][n - 1 - j] + words[y][j] == 5).only_enforce_if(d.negated())
                differ.append(d)
            model.add(sum(differ) >= MIN_DIFFERENCES)

    return model, {"words": words}
