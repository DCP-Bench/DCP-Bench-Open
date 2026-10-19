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

    # Every cyclic window of length n is read as a base-k number. Each window
    # value is a separate integer variable in 0..k^n-1, tied to its digits by an
    # equality row with unit coefficient on the window variable.
    # There are exactly k^n windows, so all window values being different means
    # every length-n string occurs exactly once.
    w = [cz.Int(f"w_{i}") for i in range(length)]
    for i in range(length):
        digits = [x[(i + j) % length] * (k ** (n - 1 - j)) for j in range(n)]
        constraints.append(w[i] == cz.Sum(digits))
        constraints.append(w[i] >= 0)
        constraints.append(w[i] <= length - 1)

    # The window values are all different.
    if length >= 2:
        constraints.append(cz.Distinct(w))

    outputs = {"de_bruijn": x}
    return constraints, outputs
