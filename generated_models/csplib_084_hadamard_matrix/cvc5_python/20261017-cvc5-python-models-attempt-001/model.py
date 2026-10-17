# csplib_084_hadamard_matrix: 2cc Hadamard matrix Legendre pairs CSP for odd l.
# Variables a_1..a_l and b_1..b_l with domains {-1, +1}, m = (l - 1) / 2.
# Encoded with Boolean variables (True means +1) so every product is a sign
# comparison and the model stays linear.
import cvc5.pythonic as cz


def sign(p):
    return cz.If(p, 1, -1)


def build(instance):
    l = instance["l"]
    m = (l - 1) // 2

    pa = [cz.Bool(f"pa_{i}") for i in range(l)]
    pb = [cz.Bool(f"pb_{i}") for i in range(l)]

    constraints = []

    # c_s := PAF(A, s) + PAF(B, s) = -2, for s = 1..m, periodic indices mod l.
    # PAF(X, s) = sum_i x_i * x_{(i+s) mod l}; x_i * x_j is +1 when the signs agree.
    for s in range(1, m + 1):
        paf_a = cz.Sum([cz.If(pa[i] == pa[(i + s) % l], 1, -1) for i in range(l)])
        paf_b = cz.Sum([cz.If(pb[i] == pb[(i + s) % l], 1, -1) for i in range(l)])
        constraints.append(paf_a + paf_b == -2)

    # c_{m+1} := a_1 + ... + a_l = 1 and c_{m+2} := b_1 + ... + b_l = 1.
    constraints.append(cz.Sum([sign(p) for p in pa]) == 1)
    constraints.append(cz.Sum([sign(p) for p in pb]) == 1)

    a = [cz.If(p, 1, -1) for p in pa]
    b = [cz.If(p, 1, -1) for p in pb]
    return constraints, {"a": a, "b": b}
