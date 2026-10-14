# Problem: Work out the seat and nationality of each of three people around a circular table from the card-passing clues.
from pycsp3 import *

# seats are 0, 1, 2 around the table; seat s+1 is on the right of seat s (mod 3)
x = Var(dom=range(3))
y = Var(dom=range(3))
z = Var(dom=range(3))
american = Var(dom=range(3))
english = Var(dom=range(3))
french = Var(dom=range(3))
satisfy(
    # X, Y and Z sit in different seats
    AllDifferent([x, y, z]),
    # the American, English and French persons are different people
    AllDifferent([american, english, french]),
    # Y passed three hearts to the American, who sits on the right of Y
    american == (y + 1) % 3,
    # X passed to the person who passed to the Frenchwoman, so the French seat is two to the right of X
    french == (x + 2) % 3,
)
