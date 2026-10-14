# KenKen: fill an n x n grid with the digits 1..n so that every row and every
# column holds each digit once and every cage (a group of cells) meets its
# target. Digits may repeat inside a cage.
import itertools

from hermax.model import Model


def build(instance):
    n = instance["n"]  # grid size and largest digit
    problem = instance["problem"]  # each cage is [target, [[row, col], ...]], cells 1-based

    m = Model()
    # x[i][j] = the digit in row i, column j (the declared output)
    x = m.int_matrix("x", n, n, 1, n)

    # each row and each column contains every digit once
    for i in range(n):
        m &= x.row(i).all_different()
        m &= x.col(i).all_different()

    # Does this assignment of digits to the cells of a cage reach the target?
    # Rules are those of the problem's model: a two-cell cage may be a sum, a
    # product, a difference or an exact quotient of its two digits (either way
    # round); any other cage is the sum or the product of its digits.
    def meets(target, digits):
        if len(digits) == 2:
            a, b = digits
            return (a + b == target or a * b == target or a * target == b
                    or b * target == a or a - b == target or b - a == target)
        product = 1
        for d in digits:
            product *= d
        return sum(digits) == target or product == target

    # Each cage chooses one of the digit combinations that meets its target.
    # choice[t] is forced to mean "the cage has the t-th allowed combination",
    # and the combination fixes the digit of every cell of the cage.
    for c, (target, cells) in enumerate(problem):
        allowed = [d for d in itertools.product(range(1, n + 1), repeat=len(cells)) if meets(target, d)]
        choice = m.bool_vector(f"cage_{c}", len(allowed))
        m &= choice.at_least_one()
        for t, digits in enumerate(allowed):
            for (row, col), digit in zip(cells, digits):
                m &= (~choice[t] | (x[row - 1][col - 1] == digit))

    return m, {"x": x}
