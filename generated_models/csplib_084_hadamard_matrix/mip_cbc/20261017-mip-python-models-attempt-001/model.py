# Hadamard matrix Legendre pairs, 2cc form (csplib 084).
# Find two sequences a and b of length l, entries in {-1, +1}, with
# PAF(A, s) + PAF(B, s) = -2 for s = 1..m, m = (l - 1) / 2, where PAF is the
# periodic autocorrelation (indices taken mod l), and sum(a) = 1, sum(b) = 1.
import mip


def build(instance):
    # l comes from the instance; m = (l - 1) / 2 follows from it.
    l = instance["l"]
    m = (l - 1) // 2
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Each entry is a binary x: x = 1 means +1, x = 0 means -1, so the entry is 2x - 1.
    # Products of two +-1 entries are linearised through a binary "disagree" variable:
    # e = 1 when the two entries differ, and then u * v = 1 - 2e.
    def sequence(name):
        x = [model.add_var(f"{name}_x{i}", var_type=mip.BINARY) for i in range(l)]
        return x, [2 * xi - 1 for xi in x]

    def disagree(u, v, name):
        # e = u XOR v for binaries u, v
        e = model.add_var(name, var_type=mip.BINARY)
        model.add_constr(e >= u - v)
        model.add_constr(e >= v - u)
        model.add_constr(e <= u + v)
        model.add_constr(e + u + v <= 2)
        return e

    xa, a = sequence("a")
    xb, b = sequence("b")

    # the entries of a sum to 1
    # sum of a_1..a_l = 1
    model += mip.xsum(a) == 1
    # the entries of b sum to 1
    # sum of b_1..b_l = 1
    model += mip.xsum(b) == 1

    # the periodic autocorrelation constraints: PAF(A, s) + PAF(B, s) = -2 for s = 1..m
    # PAF(A, s) = sum_i a_i * a_{(i+s) mod l} = l - 2 * (number of i where the two entries differ),
    # so the constraint becomes: (disagreements in A at shift s) + (disagreements in B at shift s) = l + 1
    for s in range(1, m + 1):
        da = [disagree(xa[i], xa[(i + s) % l], f"da_{s}_{i}") for i in range(l)]
        db = [disagree(xb[i], xb[(i + s) % l], f"db_{s}_{i}") for i in range(l)]
        # PAF(A, s) + PAF(B, s) = -2
        model += mip.xsum(da + db) == l + 1

    return model, {"a": a, "b": b}
