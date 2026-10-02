# Word design: find num_words DNA words of length n (letters A, C, G, T as 1..4) with exactly
# four C/G letters each, every two different words differing in at least four positions, and
# every word's reverse differing in at least four positions from every word's Watson-Crick complement.
from exact import Exact


def build(instance):
    n = instance["n"]  # length of each word
    num_words = instance["num_words"]  # number of words to find
    # Letters are coded A=1, C=2, G=3, T=4, so the Watson-Crick complement of letter a is 5 - a.
    # The constants 4 below (C/G letters per word, minimum differences) belong to the problem.
    letters = (1, 2, 3, 4)
    cg_letters = 4
    min_differences = 4

    solver = Exact()

    # words[i][j] is the j-th letter of word i
    words = [[f"words_{i}_{j}" for j in range(n)] for i in range(num_words)]
    # is_letter[i][j][a] = 1 when words[i][j] == a. Exact has no element or disequality
    # constraint, so comparing letters is done through these 0/1 indicators (4 per cell).
    is_letter = [[{a: f"words_{i}_{j}_is_{a}" for a in letters} for j in range(n)]
                 for i in range(num_words)]
    for i in range(num_words):
        for j in range(n):
            solver.addVariable(words[i][j], 1, 4)
            for a in letters:
                solver.addVariable(is_letter[i][j][a], 0, 1)
            # every position holds exactly one letter, and the integer value follows it
            solver.addConstraint([(1, is_letter[i][j][a]) for a in letters], True, 1, True, 1)
            solver.addConstraint([(a, is_letter[i][j][a]) for a in letters] + [(-1, words[i][j])],
                                 True, 0, True, 0)

    # each word has exactly four letters from {C, G} (the letters 2 and 3)
    for i in range(num_words):
        solver.addConstraint([(1, is_letter[i][j][a]) for j in range(n) for a in (2, 3)],
                             True, cg_letters, True, cg_letters)

    # two different words differ in at least four positions. differs[j] may be 1 only when the
    # two words really have different letters at j: it is forced to 0 if both hold the same letter.
    for x in range(num_words):
        for y in range(x + 1, num_words):
            differs = [f"words_{x}_{y}_differ_at_{j}" for j in range(n)]
            for j in range(n):
                solver.addVariable(differs[j], 0, 1)
                for a in letters:
                    solver.addConstraint([(1, differs[j]), (1, is_letter[x][j][a]), (1, is_letter[y][j][a])],
                                         False, 0, True, 2)
            solver.addConstraint([(1, name) for name in differs], True, min_differences)

    # the reverse of any word x (letters read from the end) differs in at least four positions
    # from the Watson-Crick complement of any word y, including x == y. Position j compares
    # x[n-1-j] with 5 - y[j], so they are equal when x[n-1-j] == a and y[j] == 5 - a.
    for x in range(num_words):
        for y in range(num_words):
            differs = [f"reverse_{x}_complement_{y}_differ_at_{j}" for j in range(n)]
            for j in range(n):
                solver.addVariable(differs[j], 0, 1)
                for a in letters:
                    solver.addConstraint([(1, differs[j]), (1, is_letter[x][n - 1 - j][a]),
                                          (1, is_letter[y][j][5 - a])], False, 0, True, 2)
            solver.addConstraint([(1, name) for name in differs], True, min_differences)

    return solver, {"words": words}
