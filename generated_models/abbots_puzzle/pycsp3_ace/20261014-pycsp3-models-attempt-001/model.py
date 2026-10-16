from pycsp3 import *

# Abbot's puzzle: 100 bushels of corn are given to 100 people; men get 3 bushels each,
# women 2 bushels each, children half a bushel each. Find the number of men, women and children.

men = Var(dom=range(101))
women = Var(dom=range(101))
children = Var(dom=range(101))

satisfy(
    # there are 100 people in total
    men + women + children == 100,
    # the 100 bushels are distributed: 3 per man, 2 per woman, 1/2 per child (counted in half bushels)
    6 * men + 4 * women + children == 200,
    # there are five times as many women as men
    women == 5 * men,
)
