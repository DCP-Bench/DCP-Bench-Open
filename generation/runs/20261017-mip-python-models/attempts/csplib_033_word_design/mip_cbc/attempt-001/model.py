# Problem: csplib_033_word_design (CSPLib 33, word design over {A, C, G, T}).
# Letters are coded A=1, C=2, G=3, T=4. Complement maps v to 5 - v (A<->T, C<->G).
# Find num_words words of length n such that the words satisfy the following.
#
# Each word has exactly 4 symbols from {C, G}.
#
# Each pair of distinct words differ in at least 4 positions.
#
# Each pair of words x and y (x and y may be identical) are such that x^R and y^C
# differ in at least 4 positions, where x^R is the reverse of x and y^C the complement of y.
import mip


def build(instance):
    n = instance["n"]
    num_words = instance["num_words"]
    letters = [1, 2, 3, 4]

    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # x[k][i][c - 1] = 1 iff word k has letter c at position i (one-hot)
    x = [
        [[m.add_var(f"x_{k}_{i}_{c}", var_type=mip.BINARY) for c in letters] for i in range(n)]
        for k in range(num_words)
    ]
    # w[k][i] is the letter itself, the declared output
    w = [
        [m.add_var(f"w_{k}_{i}", lb=1, ub=4, var_type=mip.INTEGER) for i in range(n)]
        for k in range(num_words)
    ]

    def X(k, i, c):
        return x[k][i][c - 1]

    # Each position holds exactly one letter.
    for k in range(num_words):
        for i in range(n):
            m += mip.xsum(X(k, i, c) for c in letters) == 1

    # The letter variable is the value of the one-hot encoding.
    for k in range(num_words):
        for i in range(n):
            m += w[k][i] == mip.xsum(c * X(k, i, c) for c in letters)

    # Each word has exactly 4 symbols from {C, G}.
    for k in range(num_words):
        m += mip.xsum(X(k, i, c) for i in range(n) for c in (2, 3)) == 4

    # Each pair of distinct words differ in at least 4 positions.
    # d = 1 forces a difference at position i (equal letters give d = 0).
    for k in range(num_words):
        for l in range(k + 1, num_words):
            d = [m.add_var(f"d_{k}_{l}_{i}", var_type=mip.BINARY) for i in range(n)]
            for i in range(n):
                for c in letters:
                    m += d[i] + X(k, i, c) + X(l, i, c) <= 2
            m += mip.xsum(d) >= 4

    # For each pair x, y (including x = y): x^R and y^C differ in at least 4 positions.
    # Position i of x^R is letter n-1-i of x. Position i of y^C is 5 - (letter i of y).
    for k in range(num_words):
        for l in range(num_words):
            e = [m.add_var(f"e_{k}_{l}_{i}", var_type=mip.BINARY) for i in range(n)]
            for i in range(n):
                for c in letters:
                    m += e[i] + X(k, n - 1 - i, c) + X(l, i, 5 - c) <= 2
            m += mip.xsum(e) >= 4

    return m, {"words": w}
