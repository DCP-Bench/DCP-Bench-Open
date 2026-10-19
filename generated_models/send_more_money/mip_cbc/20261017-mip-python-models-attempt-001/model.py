# Send More Money: give each letter s, e, n, d, m, o, r, y a distinct digit 0..9
# so that SEND + MORE = MONEY holds, with the first letters of SEND and MORE nonzero.
# Satisfaction problem: the declared outputs are the eight digits.
import mip

LETTERS = ["s", "e", "n", "d", "m", "o", "r", "y"]


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # the first letters of SEND and MORE are nonzero
    digit = {}
    for letter in LETTERS:
        lb = 1 if letter in ("s", "m") else 0
        digit[letter] = model.add_var(letter, lb=lb, ub=9, var_type=mip.INTEGER)

    # each letter takes exactly one digit: one-hot binaries choice[letter][v]
    choice = {}
    for letter in LETTERS:
        choice[letter] = [model.add_var(f"c_{letter}_{v}", var_type=mip.BINARY) for v in range(10)]
        model += mip.xsum(choice[letter]) == 1
        model += digit[letter] == mip.xsum(v * choice[letter][v] for v in range(10))

    # each letter takes a different digit: every digit is used by at most one letter
    for v in range(10):
        model += mip.xsum(choice[letter][v] for letter in LETTERS) <= 1

    # SEND + MORE = MONEY, written as one equation over the place values
    # (the coefficients of each letter are summed over its columns: e appears in
    # the units of SEND, the units of MORE and the tens of MONEY)
    model += mip.xsum([
        1000 * digit["s"],
        91 * digit["e"],
        -90 * digit["n"],
        1 * digit["d"],
        -9000 * digit["m"],
        -900 * digit["o"],
        10 * digit["r"],
        -1 * digit["y"],
    ]) == 0

    outputs = {letter: digit[letter] for letter in LETTERS}
    return model, outputs
