# Problem: Decide who killed Aunt Agatha from the clues about hating and wealth.
from pycsp3 import *

names = data.names
A = [i for i, s in enumerate(names) if "Agatha" in s][0]
B = [i for i, s in enumerate(names) if "butler" in s][0]
C = [i for i, s in enumerate(names) if "Charles" in s][0]
# hates[p][q] = 1 if person p hates person q
hates = VarArray(size=[3, 3], dom={0, 1})
# wealth of each person, larger means richer
wealth = VarArray(size=3, dom=range(0, 10))
# index of the killer
killer = Var(dom=range(3))
satisfy(
    # Agatha hates everybody except the butler
    hates[A][A] == 1,
    hates[A][B] == 0,
    hates[A][C] == 1,
    # Charles hates no one that Agatha hates
    [imply(hates[A][q] == 1, hates[C][q] == 0) for q in range(3)],
    # the butler hates everyone whom Agatha hates
    [imply(hates[A][q] == 1, hates[B][q] == 1) for q in range(3)],
    # the butler hates everyone not richer than Aunt Agatha
    [imply(wealth[q] <= wealth[A], hates[B][q] == 1) for q in range(3)],
    # noone hates everyone
    [Sum(hates[p]) <= 2 for p in range(3)],
    # a killer always hates his victim (the victim is Agatha)
    [imply(killer == p, hates[p][A] == 1) for p in range(3)],
    # a killer is no richer than his victim
    [imply(killer == p, wealth[p] <= wealth[A]) for p in range(3)],
)
