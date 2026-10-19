# knights_tour: place the move numbers 0 .. n*n-1 on an n x n board so that
# consecutive move numbers are a knight's move apart and every square is
# visited exactly once, without returning to the starting square.
# Successor encoding: one Boolean per knight jump p -> q, plus one-hot
# "first square" and "last square" markers. The jumps form a single path.
from cvc5.pythonic import *


def exactly_one(lits):
    # at least one, and no two at once (pairwise), for Boolean literals
    clauses = [Or(lits)] if len(lits) >= 2 else [lits[0]]
    for i in range(len(lits)):
        for j in range(i + 1, len(lits)):
            clauses.append(Or(Not(lits[i]), Not(lits[j])))
    return clauses


def build(instance):
    n = instance["n"]
    N = n * n

    moves = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]

    def sq(r, c):
        return r * n + c

    nbrs = {}
    for r in range(n):
        for c in range(n):
            nbrs[sq(r, c)] = [
                sq(r + dr, c + dc)
                for dr, dc in moves
                if 0 <= r + dr < n and 0 <= c + dc < n
            ]

    s = SolverFor("QF_LIA")

    # move number of each square, 0 .. n*n-1
    x = [Int("x_%d" % p) for p in range(N)]
    for p in range(N):
        s.add(x[p] >= 0, x[p] <= N - 1)

    # one Boolean per knight jump from square p to square q
    jump = {}
    for p in range(N):
        for q in nbrs[p]:
            jump[(p, q)] = Bool("j_%d_%d" % (p, q))

    first = [Bool("f_%d" % p) for p in range(N)]
    last = [Bool("l_%d" % p) for p in range(N)]

    # the knight moves from square to square along a jump; the move
    # number goes up by one along every jump
    for (p, q), j in jump.items():
        s.add(Implies(j, x[q] == x[p] + 1))

    # the knight visits every square exactly once: each square has exactly
    # one incoming jump, or is the first square
    for q in range(N):
        incoming = [jump[(p, q)] for p in range(N) if (p, q) in jump] + [first[q]]
        for c in exactly_one(incoming):
            s.add(c)

    # and exactly one outgoing jump, or is the last square
    for p in range(N):
        outgoing = [jump[(p, q)] for q in nbrs[p]] + [last[p]]
        for c in exactly_one(outgoing):
            s.add(c)

    # the tour has one first square and one last square
    for c in exactly_one(first):
        s.add(c)
    for c in exactly_one(last):
        s.add(c)

    # the first square has move number 0 and the last square has move number n*n-1
    for p in range(N):
        s.add(Implies(first[p], x[p] == 0))
        s.add(Implies(last[p], x[p] == N - 1))

    outputs = {"x": [[x[sq(r, c)] for c in range(n)] for r in range(n)]}
    return s, outputs
