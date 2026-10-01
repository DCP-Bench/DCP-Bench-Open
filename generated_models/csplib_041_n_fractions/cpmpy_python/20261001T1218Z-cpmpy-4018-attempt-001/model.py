# CSPLib prob041, fractions: find nine distinct non-zero digits A..I such that
# A/BC + D/EF + G/HI = 1, where BC, EF and HI are two-digit numbers.
import cpmpy as cp


def build(instance):
    # The problem has no instance data: nine distinct digits from 1 to 9.
    n = 9

    # x = [A, B, C, D, E, F, G, H, I]
    x = cp.intvar(1, n, shape=(9,), name="x")
    A, B, C, D, E, F, G, H, I = x

    # The three denominators BC, EF and HI as two-digit numbers.
    den1 = cp.intvar(11, 99, name="BC")
    den2 = cp.intvar(11, 99, name="EF")
    den3 = cp.intvar(11, 99, name="HI")

    model = cp.Model()

    # The nine letters are distinct digits.
    model += cp.AllDifferent(x)

    # BC, EF and HI are the two-digit numbers written with the digits B C, E F and H I.
    model += den1 == 10 * B + C
    model += den2 == 10 * E + F
    model += den3 == 10 * H + I

    # A/BC + D/EF + G/HI = 1, multiplied through by the three denominators to stay in integers.
    model += A * den2 * den3 + D * den1 * den3 + G * den1 * den2 == den1 * den2 * den3

    return model, {"A": A, "B": B, "C": C, "D": D, "E": E, "F": F, "G": G, "H": H, "I": I}
