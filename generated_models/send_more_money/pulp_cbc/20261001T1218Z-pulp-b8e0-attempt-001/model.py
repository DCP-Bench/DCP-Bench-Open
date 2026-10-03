"""SEND + MORE = MONEY: assign different digits to the letters so that the sum holds, with
no word starting with zero.

The model reports the digit of each letter s, e, n, d, m, o, r, y.
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data

    letters = ["s", "e", "n", "d", "m", "o", "r", "y"]
    digits = range(10)

    problem = pulp.LpProblem("send_more_money", pulp.LpMinimize)  # satisfaction

    # is_digit[letter][v] = 1 if the letter stands for digit v; each letter has one digit
    # and no two letters share a digit
    is_digit = {ch: [pulp.LpVariable(f"is_{ch}_{v}", cat="Binary") for v in digits]
                for ch in letters}
    for ch in letters:
        problem += pulp.lpSum(is_digit[ch]) == 1
    for v in digits:
        problem += pulp.lpSum(is_digit[ch][v] for ch in letters) <= 1
    value = {ch: pulp.lpSum(v * is_digit[ch][v] for v in digits) for ch in letters}

    def number(word):
        return pulp.lpSum(10 ** (len(word) - 1 - k) * value[ch] for k, ch in enumerate(word))

    # SEND + MORE = MONEY
    problem += number("send") + number("more") == number("money")

    # the first letters S and M are not zero
    problem += is_digit["s"][0] == 0
    problem += is_digit["m"][0] == 0

    return problem, value
