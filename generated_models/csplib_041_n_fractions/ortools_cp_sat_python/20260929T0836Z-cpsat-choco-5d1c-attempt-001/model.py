# Fractions puzzle: find nine different non-zero digits A..I such that
# A/BC + D/EF + G/HI = 1, where BC, EF and HI are two-digit numbers.
from ortools.sat.python import cp_model


def build(instance):
    # The puzzle has no data.
    model = cp_model.CpModel()

    # the nine digits, all different and non-zero
    A, B, C, D, E, F, G, H, I = digits = [model.new_int_var(1, 9, name) for name in "ABCDEFGHI"]
    model.add_all_different(digits)

    # the three denominators BC, EF, HI as two-digit numbers
    D1 = model.new_int_var(11, 99, "D1")
    D2 = model.new_int_var(11, 99, "D2")
    D3 = model.new_int_var(11, 99, "D3")
    model.add(D1 == 10 * B + C)
    model.add(D2 == 10 * E + F)
    model.add(D3 == 10 * H + I)

    def product(x, y, hi, name):
        """A new variable equal to x * y."""
        p = model.new_int_var(0, hi, name)
        model.add_multiplication_equality(p, [x, y])
        return p

    # Multiplying the equation A/D1 + D/D2 + G/D3 = 1 through by D1*D2*D3 gives
    # A*D2*D3 + D*D1*D3 + G*D1*D2 = D1*D2*D3, which avoids fractions. CP-SAT
    # multiplies two variables at a time, so the products are built stepwise.
    D1D2 = product(D1, D2, 99 * 99, "D1D2")
    D1D3 = product(D1, D3, 99 * 99, "D1D3")
    D2D3 = product(D2, D3, 99 * 99, "D2D3")
    all_three = product(D1D2, D3, 99 * 99 * 99, "D1D2D3")
    term_a = product(A, D2D3, 9 * 99 * 99, "A_D2D3")
    term_d = product(D, D1D3, 9 * 99 * 99, "D_D1D3")
    term_g = product(G, D1D2, 9 * 99 * 99, "G_D1D2")
    model.add(term_a + term_d + term_g == all_three)

    return model, {"A": A, "B": B, "C": C, "D": D, "E": E, "F": F, "G": G, "H": H, "I": I}
