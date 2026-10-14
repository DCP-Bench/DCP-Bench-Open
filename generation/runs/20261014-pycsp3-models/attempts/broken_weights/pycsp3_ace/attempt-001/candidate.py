from pycsp3 import *

# A weight of total m pounds broke into n pieces with whole-pound weights; the pieces must
# weigh every integer from 1 to m on a balance scale (pieces may go on either pan).
m = data.m
n = data.n

# weights[i] is the whole-pound weight of piece i
weights = VarArray(size=n, dom=range(1, m + 1))

# for each target weight k, put_on[k][i] is +1 (piece i on the object's pan), -1 (piece i on the
# other pan) or 0 (piece i not used); signed[k][i] is the signed contribution of piece i to k
put_on = VarArray(size=[m, n], dom={-1, 0, 1})
signed = VarArray(size=[m, n], dom=range(-m, m + 1))

satisfy(
    # the pieces add up to the total weight
    Sum(weights) == m,
    # the pieces are listed in non-decreasing order, to break the symmetry of their order
    Increasing(weights, strict=False),
    # each piece is on one pan, on the other pan, or not used for this weighing
    [
        [
            # a piece on the object's pan contributes its weight
            imply(put_on[k][i] == 1, signed[k][i] == weights[i]),
            # a piece on the other pan contributes minus its weight
            imply(put_on[k][i] == -1, signed[k][i] == -weights[i]),
            # a piece not used contributes nothing
            imply(put_on[k][i] == 0, signed[k][i] == 0),
        ]
        for k in range(m) for i in range(n)
    ],
    # every whole weight from 1 to m can be balanced by the pieces
    [Sum(signed[k]) == k + 1 for k in range(m)],
)
