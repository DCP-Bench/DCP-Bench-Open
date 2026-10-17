# Word design (CSPLib 033) for cvc5 (pythonic API).
# Find num_words words of length n over {A,C,G,T}, coded 1=A, 2=C, 3=G, 4=T.
# Output: words[num_words][n].

import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    num_words = instance["num_words"]

    words = [[cz.Int(f"w_{i}_{k}") for k in range(n)] for i in range(num_words)]

    constraints = []

    # Letters are 1..4 (A, C, G, T).
    for row in words:
        for x in row:
            constraints.append(x >= 1)
            constraints.append(x <= 4)

    # Each word in S has 4 symbols from {C,G}.
    # C and G are the codes 2 and 3.
    for row in words:
        constraints.append(
            cz.Sum([cz.If(cz.Or(x == 2, x == 3), 1, 0) for x in row]) == 4
        )

    # Each pair of distinct words in S differ in at least 4 positions.
    for i in range(num_words):
        for j in range(i + 1, num_words):
            constraints.append(
                cz.Sum([cz.If(words[i][k] != words[j][k], 1, 0) for k in range(n)]) >= 4
            )

    # For each pair x, y in S (x and y may be equal): x reversed and y complemented
    # differ in at least 4 positions. The Watson-Crick complement maps letter v to 5 - v
    # (A<->T, C<->G). Reverse of x at position k is x[n-1-k].
    for i in range(num_words):
        for j in range(num_words):
            constraints.append(
                cz.Sum(
                    [
                        cz.If(words[i][n - 1 - k] != 5 - words[j][k], 1, 0)
                        for k in range(n)
                    ]
                )
                >= 4
            )

    outputs = {"words": words}
    return constraints, outputs
