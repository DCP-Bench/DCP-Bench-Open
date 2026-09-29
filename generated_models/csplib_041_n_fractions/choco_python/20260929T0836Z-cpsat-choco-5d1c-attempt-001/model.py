# Fractions puzzle: find nine different non-zero digits A..I such that
# A/BC + D/EF + G/HI = 1, where BC, EF and HI are two-digit numbers.
from pychoco.model import Model


def build(instance):
    # The puzzle has no data.
    model = Model()

    # the nine digits, all different and non-zero
    digits = [model.intvar(1, 9, name=letter) for letter in "ABCDEFGHI"]
    A, B, C, D, E, F, G, H, I = digits
    model.all_different(digits).post()

    # the three denominators BC, EF, HI as two-digit numbers
    D1 = model.intvar(11, 99, name="D1")
    D2 = model.intvar(11, 99, name="D2")
    D3 = model.intvar(11, 99, name="D3")
    model.scalar([B, C], [10, 1], "=", D1).post()
    model.scalar([E, F], [10, 1], "=", D2).post()
    model.scalar([H, I], [10, 1], "=", D3).post()

    def product(x, y, lo, hi, name):
        """A new variable equal to x * y."""
        p = model.intvar(lo, hi, name=name)
        model.times(x, y, p).post()
        return p

    # Multiplying the equation A/D1 + D/D2 + G/D3 = 1 through by D1*D2*D3 gives
    # A*D2*D3 + D*D1*D3 + G*D1*D2 = D1*D2*D3, which avoids fractions. Choco
    # multiplies two variables at a time, so the products are built stepwise.
    D1D2 = product(D1, D2, 11 * 11, 99 * 99, "D1D2")
    D1D3 = product(D1, D3, 11 * 11, 99 * 99, "D1D3")
    D2D3 = product(D2, D3, 11 * 11, 99 * 99, "D2D3")
    all_three = product(D1D2, D3, 11 * 11 * 11, 99 * 99 * 99, "D1D2D3")
    term_a = product(A, D2D3, 11 * 11, 9 * 99 * 99, "A_D2D3")
    term_d = product(D, D1D3, 11 * 11, 9 * 99 * 99, "D_D1D3")
    term_g = product(G, D1D2, 11 * 11, 9 * 99 * 99, "G_D1D2")
    model.scalar([term_a, term_d, term_g, all_three], [1, 1, 1, -1], "=", 0).post()

    return model, {"A": A, "B": B, "C": C, "D": D, "E": E, "F": F, "G": G, "H": H, "I": I}
