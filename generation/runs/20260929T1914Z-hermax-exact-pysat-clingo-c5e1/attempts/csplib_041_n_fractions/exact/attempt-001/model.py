# Fractions puzzle: find nine different non-zero digits A..I such that
# A/BC + D/EF + G/HI = 1, where BC, EF and HI are two-digit numbers.
from exact import Exact


def build(instance):
    # The puzzle has no data.
    solver = Exact()
    digits = list("ABCDEFGHI")
    for name in digits:
        solver.addVariable(name, 1, 9)

    # the nine digits are all different: indicators say which digit each letter
    # has, and each digit is used at most once
    is_ = {name: {d: f"{name}_is_{d}" for d in range(1, 10)} for name in digits}
    for name in digits:
        for d in range(1, 10):
            solver.addVariable(is_[name][d], 0, 1)
        solver.addConstraint([(1, is_[name][d]) for d in range(1, 10)], True, 1, True, 1)
        solver.addConstraint([(d, is_[name][d]) for d in range(1, 10)] + [(-1, name)], True, 0, True, 0)
    for d in range(1, 10):
        solver.addConstraint([(1, is_[name][d]) for name in digits], True, 1, True, 1)

    # the three denominators BC, EF, HI as two-digit numbers
    for denominator, (tens, units) in (("D1", "BC"), ("D2", "EF"), ("D3", "HI")):
        solver.addVariable(denominator, 11, 99)
        solver.addConstraint([(1, denominator), (-10, tens), (-1, units)], True, 0, True, 0)

    def product(name, factors, low, high):
        """A new variable equal to the product of the named variables."""
        solver.addVariable(name, low, high)
        solver.addMultiplication(factors, True, name, True, name)

    # Multiplying the equation A/D1 + D/D2 + G/D3 = 1 through by D1*D2*D3 gives
    # A*D2*D3 + D*D1*D3 + G*D1*D2 = D1*D2*D3, which avoids fractions. Exact
    # multiplies the named variables, so the products are built stepwise.
    product("D1D2", ["D1", "D2"], 121, 9801)
    product("D1D3", ["D1", "D3"], 121, 9801)
    product("D2D3", ["D2", "D3"], 121, 9801)
    product("D1D2D3", ["D1D2", "D3"], 1331, 970299)
    product("A_D2D3", ["A", "D2D3"], 121, 88209)
    product("D_D1D3", ["D", "D1D3"], 121, 88209)
    product("G_D1D2", ["G", "D1D2"], 121, 88209)
    solver.addConstraint([(1, "A_D2D3"), (1, "D_D1D3"), (1, "G_D1D2"), (-1, "D1D2D3")], True, 0, True, 0)

    return solver, {name: name for name in digits}
