# Problem: autoref. Given an integer n > 0 and an integer m >= 0, find a non-empty
# finite series S = (s0, s1, ..., sn, sn+1) such that (1) there are si occurrences
# of i in S for each integer i from 0 to n, and (2) sn+1 = m. Output the series S.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    m = instance["m"]
    length = n + 2  # the series has entries s0 .. sn+1
    s = [cz.Int(f"s{j}") for j in range(length)]

    solver = cz.SolverFor("QF_LIA")

    # Every entry is a count of occurrences in S, so it lies between 0 and the length.
    for v in s:
        solver.add(v >= 0, v <= length)

    # (1) there are si occurrences of i in S for each integer i from 0 to n.
    # Each indicator is a 0/1 integer, so the counts stay linear.
    for i in range(n + 1):
        indicators = [cz.If(s[j] == i, 1, 0) for j in range(length)]
        solver.add(cz.Sum(indicators) == s[i])

    # (2) sn+1 = m.
    solver.add(s[n + 1] == m)

    return solver, {"s": s}
