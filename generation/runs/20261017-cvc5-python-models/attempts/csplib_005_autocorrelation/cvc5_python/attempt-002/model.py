# Problem: csplib_005_autocorrelation. Binary sequence of length n with values +1 or -1
# that minimises the periodic autocorrelation energy E = sum_{k=1}^{n-1} C_k^2, where
# C_k = sum_{i=0}^{n-1} S_i * S_{(i+k) mod n}.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]

    # Each bit in the sequence takes the value +1 or -1.
    # A Boolean b[i] encodes it: true means +1, false means -1.
    b = cz.Bools([f"b{i}" for i in range(n)])
    s = [cz.If(b[i], 1, -1) for i in range(n)]

    constraints = []

    # The periodic k-th autocorrelation is C_k = sum_{i=0}^{n-1} S_i * S_{(i+k) mod n}.
    # For +1/-1 values the product S_i * S_j is +1 when the bits are equal and -1 otherwise,
    # which keeps the model linear.
    c = {}
    for k in range(1, n):
        c[k] = cz.Int(f"c{k}")
        constraints.append(
            c[k] == cz.Sum([cz.If(b[i] == b[(i + k) % n], 1, -1) for i in range(n)])
        )

    # The energy is E = sum_{k=1}^{n-1} C_k^2. Every one of the n products contributes to the
    # periodic C_k, so |C_k| <= n. The square is an explicit table over that range, so the
    # model stays linear.
    sq = {}
    for k in range(1, n):
        expr = cz.IntVal(0)
        for v in range(-n, n + 1):
            expr = cz.If(c[k] == v, v * v, expr)
        sq[k] = cz.Int(f"sq{k}")
        constraints.append(sq[k] == expr)

    # Minimise the sum of the squared autocorrelations.
    energy = cz.Sum([sq[k] for k in range(1, n)])

    outputs = {"sequence": s}
    return constraints, outputs, ("minimize", energy)
