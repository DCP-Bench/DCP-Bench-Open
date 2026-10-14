from pycsp3 import *

# Harriet bought four pairs of shoes at four stores, in an order; find the order of
# purchases (values 1 to 4) for each shoe and for each store.

# the four kinds of shoes, each value is the stop at which it was bought
ecruespadrilles = Var(dom=range(1, 5))
fuchsiaflats = Var(dom=range(1, 5))
purplepumps = Var(dom=range(1, 5))
suedesandals = Var(dom=range(1, 5))

# the four stores, each value is the stop at which it was visited
footfarm = Var(dom=range(1, 5))
heelsinahandcart = Var(dom=range(1, 5))
theshoepalace = Var(dom=range(1, 5))
tootsies = Var(dom=range(1, 5))

satisfy(
    # each stop is one shoe purchase, so the shoes take the four different stops
    AllDifferent([ecruespadrilles, fuchsiaflats, purplepumps, suedesandals]),
    # each stop is one store, so the stores take the four different stops
    AllDifferent([footfarm, heelsinahandcart, theshoepalace, tootsies]),
    # Harriet bought fuchsia flats at Heels in a Handcart
    fuchsiaflats == heelsinahandcart,
    # the store she visited just after buying her purple pumps was not Tootsies
    tootsies != purplepumps + 1,
    # The Foot Farm was Harriet's second stop
    footfarm == 2,
    # Two stops after leaving The Shoe Place, Harriet bought her suede sandals
    suedesandals == theshoepalace + 2,
)
