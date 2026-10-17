# csplib_041 N-fractions: find distinct non-zero digits A, B, C, D, E, F, G, H, I
# such that A / BC + D / EF + G / HI = 1, where BC, EF and HI are the two-digit
# numbers formed by B and C, E and F, and H and I.
# Products are linearised with binary bit expansions; the equation is multiplied
# by BC * EF * HI so that it is exact over integers.
import mip


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    def int_var(name, lb, ub):
        return model.add_var(name, lb=lb, ub=ub, var_type=mip.INTEGER)

    def bin_var(name):
        return model.add_var(name, var_type=mip.BINARY)

    def bits_of(name, var, nbits):
        # var == sum of 2^k * b_k, with binaries b_k
        bits = [bin_var(f"{name}_b{k}") for k in range(nbits)]
        model.add_constr(var - mip.xsum((2**k) * b for k, b in enumerate(bits)) == 0)
        return bits

    def times_bits(bits, v, v_ub, name):
        # p = u * v, where u = sum of 2^k * bits[k] and v is an integer in 0..v_ub
        p = int_var(name, 0, v_ub * (2 ** len(bits) - 1))
        terms = []
        for k, b in enumerate(bits):
            t = int_var(f"{name}_t{k}", 0, v_ub)
            model.add_constr(t - v_ub * b <= 0)
            model.add_constr(t - v <= 0)
            model.add_constr(t - v + v_ub * (1 - b) >= 0)
            terms.append((2**k) * t)
        model.add_constr(p - mip.xsum(terms) == 0)
        return p

    digit_names = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
    digit = {}
    onehot = {}
    for name in digit_names:
        # Find distinct non-zero digits: each digit is one of 1..9
        digit[name] = int_var(name, 1, 9)
        onehot[name] = [bin_var(f"p_{name}_{v}") for v in range(1, 10)]
        model.add_constr(mip.xsum(onehot[name]) == 1)
        model.add_constr(
            digit[name] - mip.xsum(v * p for v, p in zip(range(1, 10), onehot[name])) == 0
        )
    # Find distinct digits: nine digits, nine values, so each value is used once
    for v in range(9):
        model.add_constr(mip.xsum(onehot[name][v] for name in digit_names) == 1)

    # BC, EF, HI are two-digit numbers formed by B and C, E and F, and H and I
    X = int_var("BC", 11, 99)
    Y = int_var("EF", 11, 99)
    W = int_var("HI", 11, 99)
    model.add_constr(X - 10 * digit["B"] - digit["C"] == 0)
    model.add_constr(Y - 10 * digit["E"] - digit["F"] == 0)
    model.add_constr(W - 10 * digit["H"] - digit["I"] == 0)
    xb = bits_of("BC", X, 7)
    yb = bits_of("EF", Y, 7)
    wb = bits_of("HI", W, 7)
    ab = bits_of("A", digit["A"], 4)
    db = bits_of("D", digit["D"], 4)
    gb = bits_of("G", digit["G"], 4)

    # A / BC + D / EF + G / HI = 1, multiplied by BC * EF * HI:
    # A * EF * HI + D * BC * HI + G * BC * EF = BC * EF * HI
    YW = times_bits(yb, W, 99, "EFxHI")
    XW = times_bits(xb, W, 99, "BCxHI")
    XY = times_bits(xb, Y, 99, "BCxEF")
    XYW = times_bits(xb, YW, 9801, "BCxEFxHI")
    AYW = times_bits(ab, YW, 9801, "AxEFxHI")
    DXW = times_bits(db, XW, 9801, "DxBCxHI")
    GXY = times_bits(gb, XY, 9801, "GxBCxEF")
    model.add_constr(AYW + DXW + GXY - XYW == 0)

    outputs = {name: digit[name] for name in digit_names}
    return model, outputs
