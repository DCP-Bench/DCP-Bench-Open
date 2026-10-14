# General store: each letter of the sign stands for a different digit, and the
# sixteen words above the line add up to ALL WOOL.
from collections import Counter

from exact import Exact

WORDS = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
         "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"]
TOTAL = "ALLWOOL"


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    letters = sorted(set("".join(WORDS) + TOTAL))
    width = len(TOTAL)

    solver = Exact()
    # every letter is a digit
    for letter in letters:
        solver.addVariable(letter, 0, 9)

    # every letter stands for a different digit: indicators say which digit a
    # letter has, and each digit is used at most once
    is_ = {letter: {d: f"{letter}_is_{d}" for d in range(10)} for letter in letters}
    for letter in letters:
        for d in range(10):
            solver.addVariable(is_[letter][d], 0, 1)
        solver.addConstraint([(1, is_[letter][d]) for d in range(10)], True, 1, True, 1)
        solver.addConstraint([(d, is_[letter][d]) for d in range(1, 10)] + [(-1, letter)], True, 0, True, 0)
    for d in range(10):
        solver.addConstraint([(1, is_[letter][d]) for letter in letters], False, 0, True, 1)

    # The addition is done column by column, from the units up. carry[k] is what
    # column k passes on to column k + 1; at most 15 as the column adds 16 digits.
    carry = [f"carry_{k}" for k in range(width - 1)]
    for name in carry:
        solver.addVariable(name, 0, 15)
    for k in range(width):
        # how many times each letter is added in column k, less one for the letter of the total
        net = Counter(word[-1 - k] for word in WORDS if len(word) > k)
        net[TOTAL[-1 - k]] -= 1
        terms = [(count, letter) for letter, count in net.items() if count != 0]
        # digits of column k + carry in - digit of the total - 10 * carry out = 0
        if k > 0:
            terms.append((1, carry[k - 1]))
        if k < width - 1:
            terms.append((-10, carry[k]))
        solver.addConstraint(terms, True, 0, True, 0)

    return solver, {letter: letter for letter in letters}
