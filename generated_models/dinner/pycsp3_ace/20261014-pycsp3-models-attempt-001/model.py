from pycsp3 import *

# the number of grandparents, parents and children going to dinner
grandparents = Var(dom=range(1, 7))
parents = Var(dom=range(1, 11))
children = Var(dom=range(1, 41))

satisfy(
    # there must be 20 total people at dinner
    grandparents + parents + children == 20,
    # the dinner must cost $20: grandparents $3, parents $2, children $0.50
    # (costs are doubled to stay in integers: 6, 4 and 1 per person, total 40)
    6 * grandparents + 4 * parents + children == 40,
)
