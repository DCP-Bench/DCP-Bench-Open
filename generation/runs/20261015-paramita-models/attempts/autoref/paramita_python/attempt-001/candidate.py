# autoref: find a self-describing series S = (s_0, ..., s_{n+1}).
# Entries are integers; each entry is written as a one-hot block of Bools
# over the values 0..n, so an entry is the sum of value * indicator.
# Every entry lies in 0..n: an entry above n is a value that no count
# constrains, and the reference rejects such series.
from paramita.modelling import Bool


def build(instance):
    n, m = instance["n"], instance["m"]
    length = n + 2                      # S = (s_0, ..., s_{n+1})
    top = n                             # largest value an entry can take

    # one-hot Bools: x[k][v] = 1 if entry s_k equals v
    x = [[Bool(f"x_{k}_{v}") for v in range(top + 1)] for k in range(length)]
    # value 0 has coefficient 0 and is left out of the sums
    s = [sum(v * x[k][v] for v in range(1, top + 1)) for k in range(length)]

    cons = []

    # each entry of the series holds exactly one value
    for k in range(length):
        cons.append(sum(x[k]) == 1)

    # there are s_i occurrences of i in S, for each integer i from 0 to n
    for i in range(n + 1):
        cons.append(sum(x[k][i] for k in range(length)) == s[i])

    # s_{n+1} = m
    cons.append(s[n + 1] == m)

    outputs = {"s": s}
    return cons, outputs
