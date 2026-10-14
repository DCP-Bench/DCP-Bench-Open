# ISBN-13 completion: fill in the unknown digits (marked -1) so that the 13
# digits form a valid ISBN-13 starting with 978 or 979: the last digit is the
# check digit of the first twelve, computed from their sum when they are
# weighted 1, 3, 1, 3, ... (check digit = (10 - sum mod 10) mod 10).
from hermax.model import Model


def build(instance):
    isbn_init = instance["isbn_init"]  # known digits, -1 where the digit is unknown
    n = len(isbn_init)  # 13

    m = Model()
    # isbn[i] = the i-th digit (the declared output)
    isbn = m.int_vector("isbn", n, 0, 9)

    # the digits that are given
    for i in range(n):
        if isbn_init[i] != -1:
            m &= (isbn[i] == isbn_init[i])

    # the prefix is 978 or 979 (ISBN-13 rule)
    m &= (isbn[0] == 9)
    m &= (isbn[1] == 7)
    m &= (isbn[2] >= 8)

    # Check digit. Only the weighted sum modulo 10 matters, so residue[i][a] says
    # that the weighted sum of the first i digits is congruent to a modulo 10.
    # This avoids encoding the sum itself, which can reach 9 * (6 + 18) = 216.
    residue = m.bool_matrix("residue", n, 10)
    for i in range(n):
        m &= residue.row(i).exactly_one()
    m &= residue[0][0]
    for i in range(n - 1):
        weight = 1 if i % 2 == 0 else 3  # digits are weighted 1, 3, 1, 3, ...
        for a in range(10):
            for digit in range(10):
                m &= (~residue[i][a] | ~(isbn[i] == digit) | residue[i + 1][(a + weight * digit) % 10])
    # the last digit is the check digit of the first n - 1
    for a in range(10):
        m &= (~residue[n - 1][a] | (isbn[n - 1] == (10 - a) % 10))

    return m, {"isbn": isbn}
