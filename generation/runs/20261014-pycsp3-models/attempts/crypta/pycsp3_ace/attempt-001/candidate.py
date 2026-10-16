from pycsp3 import *

# Cryptarithmetic puzzle: BAIJJAJIIAHFCFEBBJEA + DHFGABCDIDBIFFAGFEJE = GJEGACDDHFAFJBFIHEEF,
# where every letter is a distinct digit from 0 to 9 and the first letter of each number is not 0.

# one digit per letter; the first letters B, D and G are not zero
# lowercase names: ACE returned no solution for the upper-case names, so each output is an alias
a = Var(dom=range(10))
c = Var(dom=range(10))
e = Var(dom=range(10))
f = Var(dom=range(10))
h = Var(dom=range(10))
i = Var(dom=range(10))
j = Var(dom=range(10))
b = Var(dom=range(1, 10))
d = Var(dom=range(1, 10))
g = Var(dom=range(1, 10))
A, B, C, D, E, F, G, H, I, J = a, b, c, d, e, f, g, h, i, j

# the digits of the first addend, from left to right
first = [B, A, I, J, J, A, J, I, I, A, H, F, C, F, E, B, B, J, E, A]
# the digits of the second addend, from left to right
second = [D, H, F, G, A, B, C, D, I, D, B, I, F, F, A, G, F, E, J, E]
# the digits of the sum, from left to right
total = [G, J, E, G, A, C, D, D, H, F, A, F, J, B, F, I, H, E, E, F]

# carry[j] is the carry into column j, counted from the right; column 0 is the rightmost
carry = VarArray(size=21, dom={0, 1})

satisfy(
    # all letters stand for different digits
    AllDifferent([a, b, c, d, e, f, g, h, i, j]),
    # there is no carry into the rightmost column, and no carry out of the leftmost column
    carry[0] == 0,
    carry[20] == 0,
    # the columns add up from right to left, with carries
    [first[19 - j] + second[19 - j] + carry[j] == total[19 - j] + 10 * carry[j + 1]
     for j in range(20)],
)
