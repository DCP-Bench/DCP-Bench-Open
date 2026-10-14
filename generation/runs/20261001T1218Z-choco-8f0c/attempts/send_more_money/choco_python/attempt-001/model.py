# SEND + MORE = MONEY: assign distinct digits to the letters so that the sum holds and no word
# starts with zero.
from pychoco.model import Model

# The puzzle has no instance data; the three words are its statement.


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    names = "sendmory"
    digit = {L: model.intvar(0, 9, name=L) for L in names}
    s, e, n, d, m, o, r, y = (digit[L] for L in names)

    # Each letter is a different digit.
    model.all_different(list(digit.values())).post()

    # SEND + MORE = MONEY, as one linear equation with each letter's place values collected:
    # S: 1000; E: 100 + 1 - 10; N: 10 - 100; D: 1; M: 1000 - 10000; O: 100 - 1000; R: 10; Y: -1.
    model.scalar([s, e, n, d, m, o, r, y],
                 [1000, 91, -90, 1, -9000, -900, 10, -1], "=", 0).post()

    # The first letter of each word is not zero.
    model.arithm(s, ">", 0).post()
    model.arithm(m, ">", 0).post()

    return model, digit
