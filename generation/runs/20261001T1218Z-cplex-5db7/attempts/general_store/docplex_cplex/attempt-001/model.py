"""General store cryptarithm: the sixteen words on the sign add up to ALL WOOL; each letter is
a different digit.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data; the words come from the statement.
    letters = "CHESABOWPL"
    addends = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
               "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"]
    total = "ALLWOOL"
    digits = range(10)

    model = Model("general_store")

    # is_digit[c, d] is 1 when letter c stands for digit d; each letter is one digit and
    # different letters are different digits.
    is_digit = {(c, d): model.binary_var(name=f"{c}_is_{d}") for c in letters for d in digits}
    for c in letters:
        model.add_constraint(model.sum(is_digit[c, d] for d in digits) == 1)
    for d in digits:
        model.add_constraint(model.sum(is_digit[c, d] for c in letters) <= 1)
    value = {c: model.integer_var(0, 9, name=c) for c in letters}
    for c in letters:
        model.add_constraint(value[c] == model.sum(d * is_digit[c, d] for d in digits))

    def word(w):
        # The number a word spells, most significant letter first.
        return model.sum(10 ** (len(w) - 1 - k) * value[ch] for k, ch in enumerate(w))

    # The words above the line add up to ALL WOOL.
    model.add_constraint(model.sum(word(w) for w in addends) == word(total))

    return model, dict(value)
