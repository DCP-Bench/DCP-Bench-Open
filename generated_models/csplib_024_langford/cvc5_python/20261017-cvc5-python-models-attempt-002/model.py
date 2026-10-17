# Langford's problem (CSPLib 024), cvc5 (pythonic) model, Boolean encoding.
#
# Two sets of the numbers 1..k. Arrange the 2k numbers into one sequence where
# the two 1's are one number apart, the two 2's are two numbers apart, ...,
# and the two k's are k numbers apart. Output sol: the sequence of 2k values.
#
# start[v][i] is true when the two copies of v sit at positions i and i+v+1.

from cvc5.pythonic import Bool, Int, Or, And, Not, Implies


def build(instance):
    k = instance["k"]
    n = 2 * k

    # Output sequence: sol[p] in 1..k.
    sol = [Int(f"sol_{p}") for p in range(n)]

    constraints = []

    for p in range(n):
        constraints.append(And(sol[p] >= 1, sol[p] <= k))

    # One start position per value: the first copy of v is at i, the second at i+v+1,
    # both inside the sequence.
    start = {}
    for v in range(1, k + 1):
        starts = []
        for i in range(0, n - v - 1):
            b = Bool(f"s_{v}_{i}")
            start[(v, i)] = b
            starts.append(b)
        # Each number appears as one pair: exactly one start position for v.
        constraints.append(Or(starts))
        for a in range(len(starts)):
            for c in range(a + 1, len(starts)):
                constraints.append(Not(And(starts[a], starts[c])))

    # Every position of the sequence is covered by exactly one number's pair.
    for p in range(n):
        covers = []
        for v in range(1, k + 1):
            i = p
            if (v, i) in start:
                covers.append(start[(v, i)])
            j = p - v - 1
            if (v, j) in start:
                covers.append(start[(v, j)])
        constraints.append(Or(covers))
        for a in range(len(covers)):
            for c in range(a + 1, len(covers)):
                constraints.append(Not(And(covers[a], covers[c])))

    # Each pair of copies of v carries the value v at its two positions.
    for (v, i), b in start.items():
        constraints.append(Implies(b, And(sol[i] == v, sol[i + v + 1] == v)))

    outputs = {"sol": sol}
    return constraints, outputs
