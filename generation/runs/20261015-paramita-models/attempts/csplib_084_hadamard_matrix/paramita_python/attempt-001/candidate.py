"""Hadamard matrix Legendre pairs: two sequences A and B of odd length l
with entries -1 or +1 whose periodic autocorrelations sum to -2 at every
shift s = 1..m, where m = (l-1)/2, with the entries of A and of B each
summing to 1.

Encoding: each entry is a Bool that is true when the entry is +1. For a shift
s, the product a_i * a_{i+s} is +1 exactly when the two signs agree, so the
periodic autocorrelation is PAF(A,s) = 2 * E_A(s) - l, where E_A(s) counts
the agreeing pairs. The shift constraint then reads E_A(s) + E_B(s) = l - 1."""

from paramita.modelling import Bool, Iff


def build(instance):
    l = instance["l"]
    m = (l - 1) // 2
    plus = (l + 1) // 2  # a sequence of l entries in {-1,+1} sums to 1 when (l+1)/2 entries are +1
    cons = []

    # Variables: a[i] (and b[i]) is true when the entry is +1.
    a = [Bool(f"a_{i}") for i in range(l)]
    b = [Bool(f"b_{i}") for i in range(l)]

    # c_{m+1}: a_1 + ... + a_l = 1, so (l+1)/2 entries are +1.
    cons.append(sum(a) == plus)
    # c_{m+2}: b_1 + ... + b_l = 1.
    cons.append(sum(b) == plus)

    # c_s: PAF(A,s) + PAF(B,s) = -2 for s = 1..m.
    for s in range(1, m + 1):
        agree_a = [Bool(f"agree_a_{s}_{i}") for i in range(l)]
        agree_b = [Bool(f"agree_b_{s}_{i}") for i in range(l)]
        for i in range(l):
            j = (i + s) % l  # the index i+s wraps modulo l
            # agree = +1 exactly when the two entries have the same sign (product +1)
            cons.append(Iff(agree_a[i], Iff(a[i], a[j])))
            cons.append(Iff(agree_b[i], Iff(b[i], b[j])))
        # PAF(A,s) + PAF(B,s) = 2*(E_A + E_B) - 2l = -2, i.e. E_A + E_B = l - 1.
        cons.append(sum(agree_a) + sum(agree_b) == l - 1)

    # Output: the entries as -1 / +1 integers.
    return cons, {"a": [2 * x - 1 for x in a], "b": [2 * x - 1 for x in b]}
