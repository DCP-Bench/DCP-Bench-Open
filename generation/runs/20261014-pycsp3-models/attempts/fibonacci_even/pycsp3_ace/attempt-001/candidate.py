from pycsp3 import *

# Sum of the even-valued terms of the Fibonacci sequence starting 1, 2 (1, 2, 3, 5, 8, ...)
# that do not exceed four million.
# Every third term is even and each even term is 4 times the previous even term plus the one before it.
# The even terms are modelled directly, so the domains stay small.
# There are eleven even terms up to four million; the next one, 14930352, is above the bound.

res = Var(dom=range(0, 5000001))

# the even terms, starting from 2 and 8
evens = [Var(dom=range(0, 1000000), id=f"e{k}") for k in range(10)] + [Var(dom=range(0, 4000001), id="e10")]

# the first two even-valued terms are 2 and 8
satisfy(
    evens[0] == 2,
    evens[1] == 8,
)

# each even term is 4 times the previous even term plus the term before it
satisfy(evens[k] == 4 * evens[k - 1] + evens[k - 2] for k in range(2, 11))

# print the sum of all the even-valued terms which do not exceed four million (res)
satisfy(res == Sum(evens))
