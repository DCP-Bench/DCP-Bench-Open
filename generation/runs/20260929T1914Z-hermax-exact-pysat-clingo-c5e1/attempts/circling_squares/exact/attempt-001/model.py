# Circling the squares: place a different number from 1 to 99 in each of ten
# squares of a circle so that the sum of the squares of any two adjacent numbers
# equals the sum of the squares of the two numbers opposite them. A, B, F and G
# are given.
from exact import Exact

LETTERS = "ABCDEFGHIK"
GIVEN = {"A": 16, "B": 2, "F": 8, "G": 14}
# each row: the squares of the first two numbers add up to the squares of the last two
EQUATIONS = [("A", "B", "F", "G"), ("B", "C", "G", "H"), ("C", "D", "H", "I"),
             ("D", "E", "I", "K"), ("E", "F", "K", "A")]


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    solver = Exact()
    for letter in LETTERS:
        solver.addVariable(letter, 1, 99)

    # the numbers are all different: indicators say which value a number has, and
    # each value is used at most once
    is_ = {letter: {v: f"{letter}_is_{v}" for v in range(1, 100)} for letter in LETTERS}
    for letter in LETTERS:
        for v in range(1, 100):
            solver.addVariable(is_[letter][v], 0, 1)
        solver.addConstraint([(1, is_[letter][v]) for v in range(1, 100)], True, 1, True, 1)
        solver.addConstraint([(v, is_[letter][v]) for v in range(1, 100)] + [(-1, letter)], True, 0, True, 0)
    for v in range(1, 100):
        solver.addConstraint([(1, is_[letter][v]) for letter in LETTERS], False, 0, True, 1)

    # the numbers that are given
    for letter, value in GIVEN.items():
        solver.addConstraint([(1, letter)], True, value, True, value)

    # square[letter] = the number times itself
    for letter in LETTERS:
        solver.addVariable(f"square_{letter}", 1, 99 * 99)
        solver.addMultiplication([letter, letter], True, f"square_{letter}", True, f"square_{letter}")

    # adjacent pair squares = opposite pair squares
    for a, b, c, d in EQUATIONS:
        solver.addConstraint([(1, f"square_{a}"), (1, f"square_{b}"), (-1, f"square_{c}"), (-1, f"square_{d}")],
                             True, 0, True, 0)

    return solver, {letter: letter for letter in LETTERS}
