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

    # Entry s_i for i <= n counts the occurrences of i in S. Such a count cannot
    # exceed n+1: a count of length n+2 would force every entry to equal i, which
    # would make s_i = i and n+2 = i, impossible for i <= n.
    for i in range(n + 1):
        solver.add(s[i] >= 0, s[i] <= n + 1)

    # sn+1 = m is the last entry; m is the instance's own value.
    solver.add(s[n + 1] == m)

    # (1) there are si occurrences of i in S for each integer i from 0 to n.
    # Each indicator is 0/1 and the counts are linear in them.
    for i in range(n + 1):
        solver.add(cz.Sum([cz.If(s[j] == i, 1, 0) for j in range(length)]) == s[i])

    return solver, {"s": s}
