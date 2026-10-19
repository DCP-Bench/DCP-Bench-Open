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

    # Boolean indicators: at[j][v] holds exactly when entry s_j equals value v.
    # Booleans let the solver branch on the indicators instead of on integer terms.
    at = [[cz.Bool(f"at_{j}_{v}") for v in range(length + 1)] for j in range(length)]
    for j in range(length):
        for v in range(length + 1):
            solver.add(at[j][v] == (s[j] == v))
        solver.add(cz.Or(*at[j]))

    # (1) there are si occurrences of i in S for each integer i from 0 to n.
    for i in range(n + 1):
        solver.add(cz.Sum([cz.If(at[j][i], 1, 0) for j in range(length)]) == s[i])

    # (2) sn+1 = m.
    solver.add(s[n + 1] == m)

    return solver, {"s": s}
