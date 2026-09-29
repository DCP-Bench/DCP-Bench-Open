# SEND + MORE = MONEY: give each letter a different digit, with no leading zero
# in SEND, MORE or MONEY, so that the addition is correct.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    pool = IDPool()
    # a letter is a digit; S and M start a word, so they are not zero
    letters = {name: Integer(name, 1 if name in "sm" else 0, 9, vpool=pool) for name in "sendmory"}
    s, e, n, d, m, o, r, y = (letters[name] for name in "sendmory")
    engine = IntegerEngine(vars=list(letters.values()), vpool=pool)

    # every letter stands for a different digit
    engine.add_alldifferent(list(letters.values()))

    # SEND + MORE = MONEY, each word read as a number
    engine.add_linear(1000 * s + 100 * e + 10 * n + d + 1000 * m + 100 * o + 10 * r + e
                      == 10000 * m + 1000 * o + 100 * n + 10 * e + y)

    return engine.clausify(), letters
