# Problem: autoref. Given an integer n > 0 and an integer m >= 0, find a non-empty
# finite series S = (s0, s1, ..., sn, sn+1) such that (1) there are si occurrences
# of i in S for each integer i from 0 to n, and (2) sn+1 = m. Output the series S.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    m = instance["m"]
    length = n + 2  # the series has entries s0 .. sn+1
    s = [cz.Int(f"s{j}") for j in range(length)]

    constraints = []

    # Every entry is a count of occurrences in S, so it lies between 0 and the length.
    for v in s:
        constraints += [v >= 0, v <= length]

    # (1) there are si occurrences of i in S for each integer i from 0 to n.
    for i in range(n + 1):
        constraints.append(cz.Sum([cz.If(s[j] == i, 1, 0) for j in range(length)]) == s[i])

    # (2) sn+1 = m.
    constraints.append(s[n + 1] == m)

    return constraints, {"s": s}
