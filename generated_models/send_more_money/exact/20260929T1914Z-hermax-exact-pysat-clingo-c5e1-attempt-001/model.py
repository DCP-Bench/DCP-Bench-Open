# SEND + MORE = MONEY: give each letter a different digit, with no leading zero
# in SEND, MORE or MONEY, so that the addition is correct.
from exact import Exact


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    solver = Exact()
    letters = list("sendmory")
    for letter in letters:
        # a letter is a digit; S and M start a word, so they are not zero
        solver.addVariable(letter, 1 if letter in "sm" else 0, 9)

    # every letter stands for a different digit: indicators say which digit a
    # letter has, and each digit is used at most once
    is_ = {letter: {d: f"{letter}_is_{d}" for d in range(10)} for letter in letters}
    for letter in letters:
        for d in range(10):
            solver.addVariable(is_[letter][d], 0, 1)
        solver.addConstraint([(1, is_[letter][d]) for d in range(10)], True, 1, True, 1)
        solver.addConstraint([(d, is_[letter][d]) for d in range(10)] + [(-1, letter)], True, 0, True, 0)
    for d in range(10):
        solver.addConstraint([(1, is_[letter][d]) for letter in letters], False, 0, True, 1)

    # SEND + MORE = MONEY, each word read as a number
    solver.addConstraint(
        [(1000, "s"), (100, "e"), (10, "n"), (1, "d"), (1000, "m"), (100, "o"), (10, "r"), (1, "e"),
         (-10000, "m"), (-1000, "o"), (-100, "n"), (-10, "e"), (-1, "y")],
        True, 0, True, 0)

    return solver, {name: name for name in letters}
