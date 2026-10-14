from pycsp3 import *

n = data.n
# the weights of the pairwise combinations, in numerical order
weights = data.weights
m = len(weights)
pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]

# the weight of each bale, in increasing order
bales = VarArray(size=n, dom=range(0, max(weights) + 1))

# the weight of each pair of bales
pair_sums = VarArray(size=m, dom=range(0, 2 * max(weights) + 1))

# the weight of a pair of bales is the sum of their two weights
satisfy(
    [pair_sums[k] == bales[i] + bales[j] for k, (i, j) in enumerate(pairs)],
)

# each recorded combination weight belongs to a different pair of bales
which = VarArray(size=m, dom=range(m))
satisfy(
    AllDifferent(which),
    # the recorded weights are the pair weights, in any order
    [pair_sums[which[k]] == weights[k] for k in range(m)],
)

# the bales are listed in increasing order
satisfy(Increasing(bales, strict=False))
