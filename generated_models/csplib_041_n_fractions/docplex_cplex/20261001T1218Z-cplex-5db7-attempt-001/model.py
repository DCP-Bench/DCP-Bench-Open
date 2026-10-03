"""CSPLib 41, n-fractions puzzle: find distinct non-zero digits A..I with
A / BC + D / EF + G / HI = 1, where BC, EF and HI are two-digit numbers.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data. Digits are 1..9 and the two-digit numbers lie in
    # 1..81 (= 9 * 9), the domain the reference declares for them.
    n = 9
    digits = range(1, n + 1)
    letters = "ABCDEFGHI"
    top = n * n            # bound on BC, EF, HI
    top2 = top * top       # bound on a product of two of them

    model = Model("n_fractions")
    # The products below are linearised with bounds of up to 6561; with CPLEX's default
    # integrality tolerance (1e-5) a "zero" binary could let such a product carry about
    # 0.07, so integer values are required exactly.
    model.parameters.mip.tolerances.integrality = 0

    # is_digit[l, v] is 1 when letter l is digit v; the nine letters are distinct digits.
    is_digit = {(l, v): model.binary_var(name=f"{l}_is_{v}") for l in letters for v in digits}
    for l in letters:
        model.add_constraint(model.sum(is_digit[l, v] for v in digits) == 1)
    for v in digits:
        model.add_constraint(model.sum(is_digit[l, v] for l in letters) <= 1)
    value = {l: model.integer_var(1, n, name=l) for l in letters}
    for l in letters:
        model.add_constraint(value[l] == model.sum(v * is_digit[l, v] for v in digits))

    # The two-digit numbers BC, EF and HI.
    def two_digit(tens, units, name):
        number = model.integer_var(1, top, name=name)
        model.add_constraint(number == 10 * value[tens] + value[units])
        return number

    D1 = two_digit("B", "C", "BC")
    D2 = two_digit("E", "F", "EF")
    D3 = two_digit("H", "I", "HI")

    # letter * factor for a factor in 0..hi, written as sum over the digits v of
    # v * (factor if the letter is v, else 0); each term is the product of a binary and a
    # bounded integer, which has a linear encoding. CPLEX refuses a product of two variables.
    def times(letter, factor, hi, name):
        terms = []
        for v in digits:
            b = is_digit[letter, v]
            p = model.integer_var(0, hi, name=f"{name}_{v}")
            model.add_constraint(p <= hi * b)
            model.add_constraint(p <= factor)
            model.add_constraint(p >= factor - hi * (1 - b))
            terms.append(v * p)
        return model.sum(terms)

    # product of a two-digit number tens*10 + units with a factor in 0..hi.
    def times_number(tens, units, factor, hi, name):
        return (10 * times(tens, factor, hi, f"{name}_t")
                + times(units, factor, hi, f"{name}_u"))

    def product(expr, name):
        var = model.integer_var(0, top2, name=name)
        model.add_constraint(var == expr)
        return var

    EF_HI = product(times_number("E", "F", D3, top, "EF_HI"), "EF_times_HI")
    BC_HI = product(times_number("B", "C", D3, top, "BC_HI"), "BC_times_HI")
    BC_EF = product(times_number("B", "C", D2, top, "BC_EF"), "BC_times_EF")

    # Multiplying A / BC + D / EF + G / HI = 1 by BC * EF * HI:
    # A * EF * HI + D * BC * HI + G * BC * EF == BC * EF * HI.
    model.add_constraint(
        times("A", EF_HI, top2, "A_EF_HI") + times("D", BC_HI, top2, "D_BC_HI")
        + times("G", BC_EF, top2, "G_BC_EF")
        == times_number("B", "C", EF_HI, top2, "BC_EF_HI"))

    return model, dict(value)
