# csplib_041_n_fractions: N fractions.
# Find distinct non-zero digits (A, B, C, D, E, F, G, H, I) such that
# A / BC + D / EF + G / HI = 1, where BC, EF and HI are the two-digit numbers
# formed by B and C, E and F, and H and I.
import cvc5.pythonic as cz


def build(instance):
    A, B, C, D, E, F, G, H, I = cz.Ints("A B C D E F G H I")
    digits = [A, B, C, D, E, F, G, H, I]

    # two-digit numbers, linear in their digits
    X = 10 * B + C
    Y = 10 * E + F
    Z = 10 * H + I

    constraints = []
    aux = []  # product definitions, collected below

    # the nine digits are distinct and non-zero
    constraints += [d >= 1 for d in digits]
    constraints += [d <= 9 for d in digits]
    constraints.append(cz.Distinct(digits))

    # A digit times a linear term, as a case split on the digit (no nonlinear terms)
    def mul(name, d, t):
        p = cz.Int(name)
        aux.append(cz.Or([cz.And(d == a, p == a * t) for a in range(1, 10)]))
        return p

    # YZ = EF * HI, XZ = BC * HI, XY = BC * EF, each split into digit products
    YZ = cz.Int("YZ")
    XZ = cz.Int("XZ")
    XY = cz.Int("XY")
    aux.append(YZ == 10 * mul("EZ", E, Z) + mul("FZ", F, Z))
    aux.append(XZ == 10 * mul("BZ", B, Z) + mul("CZ", C, Z))
    aux.append(XY == 10 * mul("BY", B, Y) + mul("CY", C, Y))

    # A/BC + D/EF + G/HI = 1, multiplied by BC * EF * HI:
    # A*YZ + D*XZ + G*XY = X*YZ
    lhs = mul("AYZ", A, YZ) + mul("DXZ", D, XZ) + mul("GXY", G, XY)
    rhs = 10 * mul("BYZ", B, YZ) + mul("CYZ", C, YZ)
    aux.append(lhs == rhs)

    constraints += aux

    outputs = {"A": A, "B": B, "C": C, "D": D, "E": E, "F": F, "G": G, "H": H, "I": I}
    return constraints, outputs
