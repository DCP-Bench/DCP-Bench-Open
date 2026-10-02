# ISBN-13: complete the unknown digits (-1) of a 13-digit ISBN so that it starts with 978 or 979
# and its last digit is the correct check digit for the first 12 digits.
from exact import Exact


def build(instance):
    isbn_init = instance["isbn_init"]  # the given digits, -1 for an unknown digit
    n = len(isbn_init)

    solver = Exact()

    # isbn[i] is digit i, from 0 to 9. The prefix is 9, 7 and then 8 or 9, which narrows the
    # first three domains.
    isbn = [f"isbn_{i}" for i in range(n)]
    prefix_domains = {0: (9, 9), 1: (7, 7), 2: (8, 9)}
    for i in range(n):
        low, high = prefix_domains.get(i, (0, 9))
        solver.addVariable(isbn[i], low, high)

    # the digits that are given
    for i in range(n):
        if isbn_init[i] != -1:
            solver.addConstraint([(1, isbn[i])], True, isbn_init[i], True, isbn_init[i])

    # Check digit: the first 12 digits are weighted alternately 1 and 3, and the check digit is
    # (10 - (sum mod 10)) mod 10. For a digit in 0..9 that is the same as saying that the
    # weighted sum plus the check digit is a multiple of 10: weighted sum + check = 10 * tens.
    weights = [1 if i % 2 == 0 else 3 for i in range(n - 1)]
    max_total = 9 * sum(weights) + 9  # largest possible value of the weighted sum plus the check digit
    solver.addVariable("tens", 0, max_total // 10)
    solver.addConstraint([(w, isbn[i]) for i, w in enumerate(weights)] + [(1, isbn[n - 1]), (-10, "tens")],
                         True, 0, True, 0)

    return solver, {"isbn": isbn}
