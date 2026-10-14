from pycsp3 import *

init = data.isbn_init
# the digits of the ISBN-13
isbn = VarArray(size=13, dom=range(10))
# the check digit sum is a multiple of 10: k is the quotient
k = Var(dom=range(0, 30))

satisfy(
    # an ISBN-13 must start with 978 or 979
    isbn[0] == 9,
    isbn[1] == 7,
    Or(isbn[2] == 8, isbn[2] == 9),
    # the known digits keep their values, unknown digits are given as -1
    [isbn[i] == init[i] for i in range(13) if init[i] != -1],
    # multiply the first 12 digits alternately by 1 and 3, add the check digit, and the sum is a multiple of 10
    Sum(isbn[i] * (1 if i % 2 == 0 else 3) for i in range(12)) + isbn[12] == 10 * k,
)
