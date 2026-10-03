# Hadamard matrix (Legendre pairs): find two sequences a and b of length l with entries
# -1 or +1, each summing to 1, such that for every shift s = 1..(l-1)/2 the periodic
# autocorrelations of a and b at shift s add up to -2.
from pychoco.model import Model


def build(instance):
    l = instance["l"]  # length of each sequence (odd)
    m = (l - 1) // 2  # number of shifts that get a constraint

    model = Model()

    # a[i], b[i] are the entries of the two sequences, each -1 or +1.
    # They are modelled through 0/1 variables (1 means +1), because an entry
    # pair then multiplies to +1 when the 0/1 values agree and to -1 when they differ.
    a_bit = [model.boolvar(name=f"a_bit_{i}") for i in range(l)]
    b_bit = [model.boolvar(name=f"b_bit_{i}") for i in range(l)]
    a = [model.intvar([-1, 1], name=f"a_{i}") for i in range(l)]
    b = [model.intvar([-1, 1], name=f"b_{i}") for i in range(l)]
    for entries, bits in ((a, a_bit), (b, b_bit)):
        for entry, bit in zip(entries, bits):
            model.scalar([bit, entry], [2, -1], "=", 1).post()  # entry = 2 * bit - 1

    # each sequence sums to 1: with l odd that means (l + 1) / 2 entries equal +1
    model.sum(a, "=", 1).post()
    model.sum(b, "=", 1).post()

    # periodic autocorrelation: PAF(a, s) + PAF(b, s) = -2 for s = 1..m, where
    # PAF(a, s) = sum over i of a[i] * a[(i + s) mod l].
    # The 2l products are +1 (equal entries) or -1 (different entries), so with D the
    # number of products that are -1, the sum is (2l - D) - D = -2, which means D = l + 1.
    for s in range(1, m + 1):
        different = []
        for bits in (a_bit, b_bit):
            for i in range(l):
                different.append(model.arithm(bits[i], "!=", bits[(i + s) % l]).reify())
        model.sum(different, "=", l + 1).post()

    return model, {"a": a, "b": b}
