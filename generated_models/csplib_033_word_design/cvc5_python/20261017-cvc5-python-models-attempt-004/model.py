# Word design (CSPLib 033) for cvc5 (pythonic API), one-hot Boolean letters.
# Find num_words words of length n over {A,C,G,T}, coded 1=A, 2=C, 3=G, 4=T.
# Output: words[num_words][n], each letter an integer 1..4.

import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    num_words = instance["num_words"]
    letters = [1, 2, 3, 4]

    # b[i][k][v]: word i has letter v (1..4) at position k.
    b = [
        [[cz.Bool(f"b_{i}_{k}_{v}") for v in letters] for k in range(n)]
        for i in range(num_words)
    ]

    s = cz.SolverFor("QF_LIA")

    # Exactly one letter per position.
    for i in range(num_words):
        for k in range(n):
            s.add(cz.Sum([cz.If(b[i][k][v], 1, 0) for v in range(4)]) == 1)

    # Each word in S has 4 symbols from {C,G}: letters 2 and 3, indices 1 and 2.
    for i in range(num_words):
        s.add(
            cz.Sum(
                [cz.If(b[i][k][v], 1, 0) for k in range(n) for v in (1, 2)]
            )
            == 4
        )

    def same(p, q):
        # p and q are (word, position, letter) triples; true when letters match.
        return cz.Or([cz.And(b[p[0]][p[1]][v], b[q[0]][q[1]][v]) for v in range(4)])

    # Each pair of distinct words in S differ in at least 4 positions.
    for i in range(num_words):
        for j in range(i + 1, num_words):
            s.add(
                cz.Sum(
                    [cz.If(cz.Not(same((i, k), (j, k))), 1, 0) for k in range(n)]
                )
                >= 4
            )

    # For each pair x, y in S (x and y may be equal): x reversed and y complemented
    # differ in at least 4 positions. The Watson-Crick complement maps letter v to 5 - v
    # (A<->T, C<->G), so index v (letter v+1) maps to index 3 - v.
    # Reverse of x at position k is x[n-1-k].
    for i in range(num_words):
        for j in range(num_words):
            s.add(
                cz.Sum(
                    [
                        cz.If(
                            cz.Not(
                                cz.Or(
                                    [
                                        cz.And(
                                            b[i][n - 1 - k][v],
                                            b[j][k][3 - v],
                                        )
                                        for v in range(4)
                                    ]
                                )
                            ),
                            1,
                            0,
                        )
                        for k in range(n)
                    ]
                )
                >= 4
            )

    # Decode the letters back to integers 1..4 for the output.
    words = [
        [
            cz.Sum([cz.If(b[i][k][v], letters[v], 0) for v in range(4)])
            for k in range(n)
        ]
        for i in range(num_words)
    ]
    outputs = {"words": words}
    return s, outputs
