from pycsp3 import *

# the choices: t = green tie, h = green hat, r = green shirt, s = green socks, n = entrance fee
t = Var(dom={0, 1})
h = Var(dom={0, 1})
r = Var(dom={0, 1})
s = Var(dom={0, 1})
n = Var(dom={0, 1})

satisfy(
    # Mr Greenguest owns a green shirt, so he wears it
    r == 1,
    # if someone wears a green tie he has to wear a green shirt
    imply(t == 1, r == 1),
    # a guest may only wear green socks and a green shirt if he wears a green tie or a green hat
    imply(And(s == 1, r == 1), Or(t == 1, h == 1)),
    # a guest wearing a green shirt or a green hat or who does not wear green socks must wear a green tie
    imply(Or(r == 1, h == 1, s == 0), t == 1),
)

# a guest who is not dressed according to rules 1 to 3 must pay the entrance fee
satisfy(
    imply(And(t == 1, r == 0), n == 1),
    imply(And(s == 1, r == 1, t == 0, h == 0), n == 1),
    imply(And(t == 0, Or(r == 1, h == 1, s == 0)), n == 1),
)

# the cheapest choice: the tie costs 10, the hat 2, the socks 12 and the entrance fee 11
minimize(10 * t + 2 * h + 12 * s + 11 * n)
