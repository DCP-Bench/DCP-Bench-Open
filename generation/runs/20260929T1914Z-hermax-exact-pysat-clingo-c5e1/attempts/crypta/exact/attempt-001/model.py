# Crypta: a cryptarithmetic addition of two 20-digit numbers. Each letter is a
# different digit from 0 to 9, and no number starts with a zero.
from collections import Counter

from exact import Exact

FIRST = "BAIJJAJIIAHFCFEBBJEA"
SECOND = "DHFGABCDIDBIFFAGFEJE"
TOTAL = "GJEGACDDHFAFJBFIHEEF"


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    letters = sorted(set(FIRST + SECOND + TOTAL))
    width = len(TOTAL)

    solver = Exact()
    # every letter is a digit, and the first letter of a number is not zero
    leading = {FIRST[0], SECOND[0], TOTAL[0]}
    for letter in letters:
        solver.addVariable(letter, 1 if letter in leading else 0, 9)

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
    # column k passes on to column k + 1, 0 or 1.
    carry = [f"carry_{k}" for k in range(width - 1)]
    for name in carry:
        solver.addVariable(name, 0, 1)
    for k in range(width):
        # the two digits of column k plus the carry in - the digit of the total - 10 * the carry out = 0
        net = Counter([FIRST[-1 - k], SECOND[-1 - k]])
        net[TOTAL[-1 - k]] -= 1
        terms = [(count, letter) for letter, count in net.items() if count != 0]
        if k > 0:
            terms.append((1, carry[k - 1]))
        if k < width - 1:
            terms.append((-10, carry[k]))
        solver.addConstraint(terms, True, 0, True, 0)

    return solver, {letter: letter for letter in letters}
