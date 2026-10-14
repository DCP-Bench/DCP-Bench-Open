from pycsp3 import *

# the ten-digit number uses each of the digits 0 to 9 exactly once
# digits[i] is the digit at position i, read from left to right
digits = VarArray(size=10, dom=range(10))
# the number formed by the digits
number = Var(dom=range(10**9, 10**10))
satisfy(
    # each digit is used exactly once
    AllDifferent(digits),
    # the number has ten digits, so its first digit is not zero
    digits[0] != 0,
    # the number is the one formed by its digits, read from left to right
    number == Sum(digits[i] * 10 ** (9 - i) for i in range(10)),
    # the number formed by the first n digits is divisible by n, for n from 1 to 10
    [Sum(digits[i] * 10 ** (n - 1 - i) for i in range(n)) % n == 0 for n in range(1, 11)],
)
