# Fractions puzzle: find nine different non-zero digits A..I such that
# A/BC + D/EF + G/HI = 1, where BC, EF and HI are two-digit numbers.
import z3


def build(instance):
    # The puzzle has no data.
    solver = z3.Solver()

    # the nine digits, all different and non-zero
    A, B, C, D, E, F, G, H, I = digits = z3.Ints("A B C D E F G H I")
    for digit in digits:
        solver.add(digit >= 1, digit <= 9)
    solver.add(z3.Distinct(digits))

    # the three denominators BC, EF, HI as two-digit numbers
    D1, D2, D3 = 10 * B + C, 10 * E + F, 10 * H + I

    # Multiplying the equation A/D1 + D/D2 + G/D3 = 1 through by D1*D2*D3 gives
    # A*D2*D3 + D*D1*D3 + G*D1*D2 = D1*D2*D3, which avoids fractions.
    solver.add(A * D2 * D3 + D * D1 * D3 + G * D1 * D2 == D1 * D2 * D3)

    return solver, {"A": A, "B": B, "C": C, "D": D, "E": E, "F": F, "G": G, "H": H, "I": I}
