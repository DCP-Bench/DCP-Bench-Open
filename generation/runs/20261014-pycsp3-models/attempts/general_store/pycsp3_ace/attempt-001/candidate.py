from pycsp3 import *

# each letter stands for a digit; the words above the line add up to ALL WOOL
c = Var(dom=range(10))
h = Var(dom=range(10))
e = Var(dom=range(10))
s = Var(dom=range(10))
a = Var(dom=range(10))
b = Var(dom=range(10))
o = Var(dom=range(10))
w = Var(dom=range(10))
p = Var(dom=range(10))
l = Var(dom=range(10))
# the output names are bound to the letter variables
C, H, E, S, A, B, O, W, P, L = c, h, e, s, a, b, o, w, p, l


def word(*letters):
    # the number written by the letters, read from left to right
    n = len(letters)
    return Sum(letter * 10 ** (n - 1 - i) for i, letter in enumerate(letters))


satisfy(
    # each different letter stands for a different digit; the description does not forbid a zero leading digit
    AllDifferent([c, h, e, s, a, b, o, w, p, l]),
    # the first letter of each word is not zero
    # the words above the line add up to the total ALL WOOL
    word(c, h, e, s, s) + word(c, a, s, h) + word(b, o, w, w, o, w) + word(c, h, o, p, s)
    + word(a, l, s, o, p, s) + word(p, a, l, e, a, l, e) + word(c, o, o, l) + word(b, a, s, s)
    + word(h, o, p, s) + word(a, l, e, s) + word(h, o, e, s) + word(a, p, p, l, e, s)
    + word(c, o, w, s) + word(c, h, e, e, s, e) + word(c, h, s, o, a, p) + word(s, h, e, e, p)
    == word(a, l, l, w, o, o, l),
)
