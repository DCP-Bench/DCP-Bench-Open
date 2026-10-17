# csplib_049_number_partitioning: partition the numbers 1..N into two sets A and B
# such that A and B have the same cardinality, the same sum, and the same sum of squares.
from cvc5.pythonic import And, If, Not, Or, Sum, Ints


def build(instance):
    n = instance["n"]
    h = n // 2
    total = n * (n + 1) // 2
    total_sq = n * (n + 1) * (2 * n + 1) // 6

    a = Ints([f"a{i}" for i in range(h)])
    b = Ints([f"b{i}" for i in range(h)])

    cons = []

    # A and B hold values from 1..N; each set is listed in increasing order.
    for x in a + b:
        cons += [x >= 1, x <= n]
    for i in range(h - 1):
        cons += [a[i] < a[i + 1], b[i] < b[i + 1]]

    # Partition 1..N: every number is in exactly one of the sets A and B.
    in_a = {}
    for j in range(1, n + 1):
        in_a[j] = Or([a[i] == j for i in range(h)])
        in_b = Or([b[i] == j for i in range(h)])
        cons += [Or(in_a[j], in_b), Not(And(in_a[j], in_b))]

    # A and B have the same cardinality.
    cons.append(Sum([If(in_a[j], 1, 0) for j in range(1, n + 1)]) == h)

    # A and B have the same sum: 2 * sum(A) = sum(1..N).
    cons.append(Sum([If(in_a[j], 2 * j, 0) for j in range(1, n + 1)]) == total)

    # A and B have the same sum of squares: 2 * sum of squares in A = sum of squares of 1..N.
    cons.append(Sum([If(in_a[j], 2 * j * j, 0) for j in range(1, n + 1)]) == total_sq)

    return cons, {"A": a, "B": b}
