# bales_of_hay: find the weights of n bales from the list of all pairwise sums.
# Each bale is a one-hot block of Bools over the values 0..W, where W is the
# largest listed weight (a bale never weighs more than the largest pair sum).
# Each pair of bales is matched to one listed weight, each weight used once.
from paramita.modelling import Bool, Iff, Or


def build(instance):
    n, weights = instance["n"], instance["weights"]
    top = max(weights)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]

    # one-hot Bools: x[i][v] = 1 if bale i weighs v
    x = [[Bool(f"bale_{i}_{v}") for v in range(top + 1)] for i in range(n)]
    # value 0 has coefficient 0 and is left out of the sums
    b = [sum(v * x[i][v] for v in range(1, top + 1)) for i in range(n)]

    cons = []

    # each bale has exactly one weight
    for i in range(n):
        cons.append(sum(x[i]) == 1)

    # the bales are printed in ascending order
    for i in range(n - 1):
        cons.append(b[i] <= b[i + 1])

    # y[(i, j, k)] = 1 when the combination of bales i and j is weighed as weights[k]
    y = {(i, j, k): Bool(f"pair_{i}_{j}_weight_{k}")
         for (i, j) in pairs for k in range(len(weights))}

    # the two bales of a combination sum to the weight it is matched to
    for (i, j) in pairs:
        for k, w in enumerate(weights):
            same_sum = [x[i][a] & x[j][w - a] for a in range(top + 1) if 0 <= w - a <= top]
            cons.append(Iff(y[(i, j, k)], Or(same_sum)))

    # every combination of two bales is matched to exactly one weight
    for (i, j) in pairs:
        cons.append(sum(y[(i, j, k)] for k in range(len(weights))) == 1)

    # every listed weight is matched to exactly one combination
    for k in range(len(weights)):
        cons.append(sum(y[(i, j, k)] for (i, j) in pairs) == 1)

    outputs = {"bales": b}
    return cons, outputs
