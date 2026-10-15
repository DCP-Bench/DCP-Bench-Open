"""Clock triplets: place the numbers 1 to 12 on the face of a clock so that
no three adjacent numbers (wrapping around 12 to 1) have a sum above 21."""

from paramita.modelling import Bool

N = 12          # numbers and clock positions (1 to 12)
LIMIT = 21      # largest allowed sum of a triplet of adjacent numbers


def build(instance):
    values = range(1, N + 1)

    # X[i][v] is true when position i of the clock holds the number v
    X = [[Bool(f"x_{i}_{v}") for v in values] for i in range(N)]
    cons = []

    # every position of the clock holds exactly one number
    for i in range(N):
        cons.append(sum(X[i]) == 1)

    # every number 1 to 12 is placed on exactly one position
    for v in range(N):
        cons.append(sum(X[i][v] for i in range(N)) == 1)

    # the value at position i, as an integer expression
    x = [sum((v + 1) * X[i][v] for v in range(N)) for i in range(N)]

    # no triplet of adjacent numbers has a sum higher than 21 (the clock wraps around)
    for i in range(N):
        cons.append(x[i] + x[(i + 1) % N] + x[(i + 2) % N] <= LIMIT)

    return cons, {"x": x}
