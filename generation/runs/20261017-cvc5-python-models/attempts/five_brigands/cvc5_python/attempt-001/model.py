# Problem five_brigands: how many doubloons each of five Spanish brigands
# (Alfonso A, Benito B, Carlos C, Diego D, Esteban E) had.

import cvc5.pythonic as cz


def build(instance):
    A, B, C, D, E = cz.Ints("A B C D E")
    outputs = {"A": A, "B": B, "C": C, "D": D, "E": E}

    # no brigand had less than one doubloon
    lower = [A >= 1, B >= 1, C >= 1, D >= 1, E >= 1]

    # The brigands captured altogether exactly 200 doubloons.
    total = [A + B + C + D + E == 200]

    # If Alfonso had twelve times as much, Benito three times as much, Carlos the same
    # amount, Diego half as much, and Esteban one-third as much, they would still have
    # altogether just 200 doubloons. Multiplied by 6 to clear the halves and thirds.
    scaled_total = [72 * A + 18 * B + 6 * C + 3 * D + 2 * E == 1200]

    return lower + total + scaled_total, outputs
