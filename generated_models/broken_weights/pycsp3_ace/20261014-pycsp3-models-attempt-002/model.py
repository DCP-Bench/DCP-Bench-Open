from pycsp3 import *

# A merchant's weight of total m pounds broke into n pieces, each a whole number of pounds, and the
# pieces must weigh every integer from 1 to m on a balance (a piece can go on either pan).
m = data.m
n = data.n

# weights[i] is the whole-pound weight of piece i
weights = VarArray(size=n, dom=range(1, m + 1))

# put_on[k][i] is +1 if piece i is on the object's pan, -1 if it is on the other pan, 0 if unused
# when weighing k; signed[k][i] is the contribution of piece i to that weighing
put_on = VarArray(size=[m, n], dom={-1, 0, 1})
signed = VarArray(size=[m, n], dom=range(-m, m + 1))

# the allowed (side, weight, contribution) triples: +w on the object's pan, -w on the other, 0 unused
signed_supports = ([(1, w, w) for w in range(1, m + 1)]
                   + [(-1, w, -w) for w in range(1, m + 1)]
                   + [(0, w, 0) for w in range(1, m + 1)])

satisfy(
    # the pieces weigh the total weight
    Sum(weights) == m,
    # the pieces are listed in non-decreasing order, which removes the order of the pieces as a symmetry
    Increasing(weights, strict=False),
    # a piece on the object's pan adds its weight, one on the other pan takes it away, an unused one adds nothing
    [Table(scope=[put_on[k][i], weights[i], signed[k][i]], supports=signed_supports)
     for k in range(m) for i in range(n)],
    # every whole weight from 1 to m can be balanced by the pieces
    [Sum(signed[k]) == k + 1 for k in range(m)],
)
