# Schur's lemma: put the balls 1..n into c boxes so that no triple of balls
# (x, y, z) with x + y = z lies entirely in one box. Solvable iff n < 14.
from paramita.modelling import Bool, Or


def build(instance):
    n, c = instance["n"], instance["c"]

    # ball i (1..n) is in box j (0..c-1); one-hot over the boxes
    # each ball is in exactly one box
    M = {i: [Bool(f"M_{i}_{j}") for j in range(c)] for i in range(1, n + 1)}
    cons = [sum(M[i]) == 1 for i in range(1, n + 1)]

    # no triple of balls x + y = z is all in the same box
    # triples are taken with x <= y, so each triple appears once; z <= n
    # when x == y the ball x appears twice, so each distinct ball appears once in the clause
    for x in range(1, n + 1):
        for y in range(x, n + 1):
            z = x + y
            if z > n:
                break
            balls = sorted({x, y, z})
            for j in range(c):
                cons.append(Or([~M[b][j] for b in balls]))

    # output: the box number (1..c) of every ball
    balls_out = [sum((j + 1) * M[i][j] for j in range(c)) for i in range(1, n + 1)]
    return cons, {"balls": balls_out}
