# de Bruijn sequence: print the de Bruijn sequence B(k, n) as a list of integers.
# A cyclic sequence over an alphabet of size k (symbols 0..k-1) of length k^n
# in which every length-n string occurs exactly once as a cyclic substring.
import cvc5.pythonic as cz


def build(instance):
    k = instance["base"]
    n = instance["n"]
    length = k ** n

    x = [cz.Int(f"x_{i}") for i in range(length)]

    constraints = []

    # The alphabet has k symbols, so every position takes a value in 0..k-1.
    # Integers are unbounded in cvc5, so the bounds are added explicitly.
    for i in range(length):
        constraints.append(x[i] >= 0)
        constraints.append(x[i] <= k - 1)

    # Every cyclic window of length n is read as a base-k number. Each window value
    # lies in 0..k^n-1, and there are exactly k^n windows, so all window values
    # being pairwise different means every length-n string occurs exactly once.
    # Keep the window values distinct, as the description asks.
    windows = []
    for i in range(length):
        w = 0
        for j in range(n):
            w = w + x[(i + j) % length] * (k ** (n - 1 - j))
        windows.append(w)

    # Distinct needs at least two terms; a single window (n = 0 or length 1) needs no check.
    if len(windows) >= 2:
        constraints.append(cz.Distinct(windows))

    outputs = {"de_bruijn": x}
    return constraints, outputs
