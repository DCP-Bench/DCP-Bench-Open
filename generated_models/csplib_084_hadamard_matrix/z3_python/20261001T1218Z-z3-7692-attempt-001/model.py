# Hadamard matrix (Legendre pairs): find two +1/-1 sequences a and b of odd
# length l, each summing to 1, whose periodic autocorrelations add up to -2 at
# every shift 1..(l-1)/2.
import z3


def build(instance):
    l = instance["l"]  # odd length of both sequences
    m = (l - 1) // 2   # number of shifts that are constrained

    a = [z3.Int(f"a_{i}") for i in range(l)]
    b = [z3.Int(f"b_{i}") for i in range(l)]

    solver = z3.Solver()

    # Every element is -1 or +1 (0 is excluded).
    for v in a + b:
        solver.add(z3.Or(v == -1, v == 1))

    # Both sequences sum to 1.
    solver.add(z3.Sum(a) == 1)
    solver.add(z3.Sum(b) == 1)

    def paf(seq, s):
        # Periodic autocorrelation at shift s: the sum of seq[i] * seq[(i + s) mod l].
        # A product of two +1/-1 values is +1 if they are equal and -1 otherwise;
        # written with If this keeps the constraint linear for Z3.
        return z3.Sum([z3.If(seq[i] == seq[(i + s) % l], 1, -1) for i in range(l)])

    # For every shift s = 1..m, the autocorrelations of a and b add up to -2.
    for s in range(1, m + 1):
        solver.add(paf(a, s) + paf(b, s) == -2)

    return solver, {"a": a, "b": b}
