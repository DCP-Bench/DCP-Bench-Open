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

    # Entry s_i for i <= n counts the occurrences of i in S. Each such entry is an
    # integer in 0..n.
    for i in range(n + 1):
        solver.add(s[i] >= 0, s[i] <= n)

    # sn+1 = m is the last entry; m is the instance's own value.
    solver.add(s[n + 1] == m)

    # (1) there are si occurrences of i in S for each integer i from 0 to n.
    # Each indicator is 0/1 and the counts are linear in them.
    for i in range(n + 1):
        solver.add(cz.Sum([cz.If(s[j] == i, 1, 0) for j in range(length)]) == s[i])

    # Redundant identity: the counts s_0 .. s_n add up to the number of entries
    # whose value lies in 0..n, since each such entry is counted by exactly one s_i.
    solver.add(
        cz.Sum([s[i] for i in range(n + 1)])
        == cz.Sum([cz.If(s[j] <= n, 1, 0) for j in range(length)])
    )

    # Redundant identity: counting by value equals counting by position, so the sum
    # of i * s_i over i in 0..n equals the sum of the entries that lie in 0..n.
    solver.add(
        cz.Sum([i * s[i] for i in range(n + 1)])
        == cz.Sum([cz.If(s[j] <= n, s[j], 0) for j in range(length)])
    )

    return solver, {"s": s}
