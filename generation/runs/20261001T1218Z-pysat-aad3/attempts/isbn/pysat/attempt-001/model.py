# ISBN-13: complete a 13-digit ISBN whose unknown digits are marked -1. It starts with 978
# or 979, and its last digit is the check digit: the first 12 digits weighted alternately 1
# and 3 are summed, and the check digit is (10 - sum mod 10) mod 10.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    isbn_init = instance["isbn_init"]  # known digits; -1 where the digit is unknown
    n = len(isbn_init)                 # 13 digits, the last one being the check digit

    pool = IDPool()
    # isbn[i] = the i-th digit
    isbn = [Integer(f"isbn{i}", 0, 9, vpool=pool) for i in range(n)]
    # multiple = the weighted sum of the first 12 digits plus the check digit, divided by 10.
    # The weighted sum is at most 9 * (6 * 1 + 6 * 3) = 216, so with the check digit (at most 9)
    # the quotient is at most 22.
    weights = [1 if i % 2 == 0 else 3 for i in range(n - 1)]
    multiple = Integer("multiple", 0, (9 * sum(weights) + 9) // 10, vpool=pool)
    engine = IntegerEngine(vars=isbn + [multiple], vpool=pool)

    # the digits that are known
    for i in range(n):
        if isbn_init[i] != -1:
            engine.add_linear(isbn[i] == isbn_init[i])

    # an ISBN-13 starts with 978 or 979
    engine.add_linear(isbn[0] == 9)
    engine.add_linear(isbn[1] == 7)
    engine.add_linear(isbn[2] >= 8)

    # check digit: it is (10 - sum mod 10) mod 10, i.e. the digit that makes the weighted sum of
    # the first 12 digits a multiple of 10 once the check digit is added (the digit is 0 to 9,
    # so it is unique)
    weighted = sum(weights[i] * isbn[i] for i in range(n - 1))
    engine.add_linear(weighted + isbn[n - 1] == 10 * multiple)

    return engine.clausify(), {"isbn": isbn}
