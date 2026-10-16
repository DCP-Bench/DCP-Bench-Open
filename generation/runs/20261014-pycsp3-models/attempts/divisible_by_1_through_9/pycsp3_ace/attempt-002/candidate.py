from pycsp3 import *

# digits[i] is the digit at position i, counted from the left
digits = VarArray(size=10, dom=range(10))
number = Var(dom=range(10**9, 10**10))
# all triples of digits (a, b, c) with 100a + 10b + c divisible by 8
div8 = [(a, b, c) for a in range(10) for b in range(10) for c in range(10) if (100 * a + 10 * b + c) % 8 == 0]
satisfy(
    # each digit is used exactly once
    AllDifferent(digits),
    # the number has ten digits, so its first digit is not zero
    digits[0] != 0,
    # the first two digits form a number divisible by 2
    Table(scope=[digits[0], digits[1]], supports=[(a, b) for a in range(10) for b in range(10) if (10 * a + b) % 2 == 0]),
    # the first three digits have a sum divisible by 3
    Sum(digits[0], digits[1], digits[2]) % 3 == 0,
    # the digits three and four form a number divisible by 4
    Table(scope=[digits[2], digits[3]], supports=[(a, b) for a in range(10) for b in range(10) if (10 * a + b) % 4 == 0]),
    # the fifth digit is zero or five, so the first five digits are divisible by 5
    Table(scope=[digits[4]], supports=[(0,), (5,)]),
    # the first six digits are divisible by 6: an even sixth digit and a digit sum divisible by 3
    Table(scope=[digits[5]], supports=[(0,), (2,), (4,), (6,), (8,)]),
    Sum(digits[i] for i in range(6)) % 3 == 0,
    # the first seven digits form a number divisible by 7
    Sum(digits[i] * 10 ** (6 - i) for i in range(7)) % 7 == 0,
    # the digits six, seven and eight form a number that, with the first five, is divisible by 8
    Table(scope=[digits[5], digits[6], digits[7]], supports=div8),
    # the first nine digits have a sum divisible by 9
    Sum(digits[i] for i in range(9)) % 9 == 0,
    # the whole number is divisible by 10, so its last digit is zero
    digits[9] == 0,
    # the number is the one formed by its digits, read from left to right
    number == Sum(digits[i] * 10 ** (9 - i) for i in range(10)),
)
