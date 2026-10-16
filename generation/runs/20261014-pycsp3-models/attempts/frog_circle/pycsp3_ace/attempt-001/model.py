from pycsp3 import *

n = data.n
# x[p] is the card at place p around the circle, with the cards 1 to n; the frog starts on card 1 at place 0
x = VarArray(size=n, dom=range(1, n + 1))
# succ[p] is the next place the frog lands on from place p; place n is a dummy place after the last card
succ = VarArray(size=n + 1, dom=range(n + 1))

satisfy(
    # the cards are different
    AllDifferent(x),
    # the frog starts on card 1 at place 0
    x[0] == 1,
    # from card k at place p the frog jumps k places clockwise
    [If(x[p] == n, Then=succ[p] == n, Else=succ[p] == (p + x[p]) % n) for p in range(n)],
    # the frog's last card is card n, which would send it back to itself, so it leaves to the dummy place
    succ[n] == 0,
    # the jumps visit every place once: one cycle through the places and the dummy place
    Circuit(succ),
)
