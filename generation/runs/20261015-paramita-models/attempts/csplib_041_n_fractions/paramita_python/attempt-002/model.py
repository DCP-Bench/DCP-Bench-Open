import itertools

from paramita.modelling import Bool, Or


# Find distinct non-zero digits A..I with A/BC + D/EF + G/HI = 1,
# where BC, EF and HI are the two-digit numbers 10*B + C, 10*E + F and 10*H + I.
#
# Encoding: each digit is one-hot over 1..9. Nine distinct non-zero digits are
# a permutation of 1..9, so every digit value is used exactly once. The fraction
# equation is a table over the digit tuples (B, C, E, F, A, D, G): for given
# BC, EF, A, D, G the number HI is forced by
#   A*EF*HI + D*BC*HI + G*BC*EF = BC*EF*HI,
# i.e. HI = G*BC*EF / (BC*EF - A*EF - D*BC). A tuple with no such two-digit HI
# is forbidden.
def build(instance):
    digits = range(1, 10)
    names = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
    one_hot = {n: {v: Bool(f"{n}_is_{v}") for v in digits} for n in names}

    cons = []

    # each digit is exactly one value
    cons += [sum(one_hot[n].values()) == 1 for n in names]

    # the nine digits are distinct: each value 1..9 is used by exactly one digit
    cons += [sum(one_hot[n][v] for n in names) == 1 for v in digits]

    # the table of the fraction equation over the digit tuples
    # (B, C, E, F, A, D, G): seven distinct digits, the remaining two are H and I
    for b, c, e, f, a, d, g in itertools.permutations(digits, 7):
        bc, ef = 10 * b + c, 10 * e + f
        den = bc * ef - a * ef - d * bc
        not_tuple = [~one_hot["B"][b], ~one_hot["C"][c], ~one_hot["E"][e],
                     ~one_hot["F"][f], ~one_hot["A"][a], ~one_hot["D"][d],
                     ~one_hot["G"][g]]
        # no two-digit HI satisfies the equation for this tuple
        if den <= 0 or (g * bc * ef) % den != 0:
            cons.append(Or(not_tuple))
            continue
        hi = g * bc * ef // den
        h, i = hi // 10, hi % 10
        if not (1 <= h <= 9 and 1 <= i <= 9):
            cons.append(Or(not_tuple))
            continue
        # the forced HI digits
        cons.append(Or(not_tuple + [one_hot["H"][h]]))
        cons.append(Or(not_tuple + [one_hot["I"][i]]))

    outputs = {n: sum(v * one_hot[n][v] for v in digits) for n in names}
    return cons, outputs
