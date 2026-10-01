# Hadamard matrix (Legendre pairs): find two sequences a and b of length l (odd), with
# entries -1 or +1, each summing to 1, whose periodic autocorrelations add up to -2
# at every shift s = 1..(l-1)/2.
import cpmpy as cp


def build(instance):
    l = instance["l"]        # sequence length, an odd positive integer
    m = (l - 1) // 2         # number of shifts that are constrained

    # Entries are -1 or +1. They are declared over -1..1 and 0 is removed below.
    a = cp.intvar(-1, 1, shape=l, name="a")
    b = cp.intvar(-1, 1, shape=l, name="b")

    def paf(seq, s):
        """Periodic autocorrelation of seq at shift s: sum of seq[i] * seq[i + s], index taken mod l."""
        return cp.sum([seq[i] * seq[(i + s) % l] for i in range(l)])

    model = cp.Model()

    # Entries are -1 or +1, never 0.
    for i in range(l):
        model += a[i] != 0
        model += b[i] != 0

    # Each sequence sums to 1.
    model += cp.sum(a) == 1
    model += cp.sum(b) == 1

    # For every shift s the two periodic autocorrelations add up to -2.
    for s in range(1, m + 1):
        model += paf(a, s) + paf(b, s) == -2

    return model, {"a": a, "b": b}
