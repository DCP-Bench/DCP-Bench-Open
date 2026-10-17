# csplib_041_n_fractions: N fractions.
# Find distinct non-zero digits (A, B, C, D, E, F, G, H, I) such that
# A / BC + D / EF + G / HI = 1, where BC, EF and HI are the two-digit numbers
# formed by B and C, E and F, and H and I.
import cvc5.pythonic as cz


def build(instance):
    A, B, C, D, E, F, G, H, I = cz.Ints("A B C D E F G H I")
    digits = [A, B, C, D, E, F, G, H, I]

    bc = 10 * B + C
    ef = 10 * E + F
    hi = 10 * H + I

    constraints = []

    # the nine digits are distinct and non-zero
    constraints += [d >= 1 for d in digits]
    constraints += [d <= 9 for d in digits]
    constraints.append(cz.Distinct(digits))

    # A / BC + D / EF + G / HI = 1, with the denominators multiplied out
    constraints.append(A * ef * hi + D * bc * hi + G * bc * ef == bc * ef * hi)

    outputs = {"A": A, "B": B, "C": C, "D": D, "E": E, "F": F, "G": G, "H": H, "I": I}
    return constraints, outputs
