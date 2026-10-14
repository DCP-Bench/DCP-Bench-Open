# General store: in the sign's addition, sixteen words add up to ALL WOOL; each letter stands for a
# different digit. Find the digits.
from pychoco.model import Model

# The puzzle has no instance data; the words of the sign are its statement.
LETTERS = "CHESABOWPL"
ADDENDS = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS", "HOPS",
           "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"]
TOTAL = "ALLWOOL"


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    # digit[L] = the digit letter L stands for
    digit = {L: model.intvar(0, 9, name=L) for L in LETTERS}

    # Different letters stand for different digits.
    model.all_different(list(digit.values())).post()

    # The words above the line add up to ALL WOOL. Each letter's place values are collected into
    # one coefficient (positive in the addends, negative in the total), so the whole sum is one
    # linear equation equal to zero.
    coefficient = {L: 0 for L in LETTERS}
    for word, sign in [(w, 1) for w in ADDENDS] + [(TOTAL, -1)]:
        for pos, L in enumerate(reversed(word)):
            coefficient[L] += sign * 10 ** pos
    model.scalar([digit[L] for L in LETTERS], [coefficient[L] for L in LETTERS], "=", 0).post()

    return model, {L: digit[L] for L in LETTERS}
