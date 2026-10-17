# Langford's problem (CSPLib 024), cvc5 (pythonic) model.
#
# Two sets of the numbers 1..k. Arrange the 2k numbers into one sequence where
# the two 1's are one number apart, the two 2's are two numbers apart, ...,
# and the two k's are k numbers apart. Output sol: the sequence of 2k values.

from cvc5.pythonic import SolverFor, Int, Ints, Distinct, Or, Implies, And


def build(instance):
    k = instance["k"]
    n = 2 * k

    # Output sequence: sol[i] in 1..k.
    sol = Ints(" ".join(f"sol_{i}" for i in range(n)))
    # Position of the first copy of value v (v = 1..k); the second copy is at
    # first + v + 1 (v numbers between them).
    first = Ints(" ".join(f"p_{v}" for v in range(1, k + 1)))

    constraints = []

    # Domains of the output sequence.
    for i in range(n):
        constraints.append(And(sol[i] >= 1, sol[i] <= k))

    # Domains of the first positions: both copies lie inside 0..2k-1.
    for v in range(1, k + 1):
        p = first[v - 1]
        constraints.append(And(p >= 0, p + v + 1 <= n - 1))

    # Positions of all 2k numbers are pairwise different.
    # Each copy of value v sits at first[v] and first[v] + v + 1.
    positions = []
    for v in range(1, k + 1):
        p = first[v - 1]
        positions.append(p)
        positions.append(p + v + 1)
    constraints.append(Distinct(positions))

    # The two copies of v appear v+1 positions apart, and the sequence holds v there.
    # Distinct positions over 2k slots fill the whole sequence.
    # Langford's pairs: the two copies of each number v are at positions p and p+v+1.
    for v in range(1, k + 1):
        p = first[v - 1]
        for i in range(n):
            constraints.append(Implies(Or(i == p, i == p + v + 1), sol[i] == v))

    outputs = {"sol": [sol[i] for i in range(n)]}
    return constraints, outputs
