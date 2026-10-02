# Low autocorrelation binary sequence: choose a sequence of n values, each +1 or -1, that
# minimises the sum over k = 1..n-1 of the squared periodic autocorrelations C_k, where
# C_k = sum_i S_i * S_((i+k) mod n).
from exact import Exact


def build(instance):
    n = instance["n"]  # length of the sequence

    solver = Exact()

    # plus[i] = 1 when S_i is +1; sequence[i] is the entry itself, -1 or +1
    plus = [f"plus_{i}" for i in range(n)]
    sequence = [f"sequence_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(plus[i], 0, 1)
        solver.addVariable(sequence[i], -1, 1)
        # the entry is 2 * plus - 1, which excludes 0
        solver.addConstraint([(1, sequence[i]), (-2, plus[i])], True, -1, True, -1)

    # same[(i, j)] = 1 exactly when S_i == S_j, for i < j. The product S_i * S_j is +1 when
    # they are equal and -1 otherwise, so a correlation is a count of equal pairs. The four
    # inequalities below make `same` the equivalence of the two 0/1 variables.
    same = {}
    for i in range(n):
        for j in range(i + 1, n):
            name = f"same_{i}_{j}"
            same[(i, j)] = name
            solver.addVariable(name, 0, 1)
            solver.addConstraint([(1, name), (1, plus[i]), (1, plus[j])], True, 1)  # both -1
            solver.addConstraint([(1, name), (-1, plus[i]), (-1, plus[j])], True, -1)  # both +1
            solver.addConstraint([(1, name), (1, plus[i]), (-1, plus[j])], False, 0, True, 1)  # +1, -1
            solver.addConstraint([(1, name), (-1, plus[i]), (1, plus[j])], False, 0, True, 1)  # -1, +1

    # The k-th periodic autocorrelation is C_k = 2 * (equal pairs) - n, where the pairs are
    # (i, (i + k) mod n). Its square cannot be written linearly, so equal_k, the number of
    # equal pairs, gets one 0/1 indicator per possible value v and the energy contribution
    # C_k^2 = (2v - n)^2 is read off the indicator that is set. Two facts about periodic
    # correlations keep the number of indicators small:
    #  - the pairs (i, i + k) and (i, i + n - k) are the same pairs, so C_k = C_(n-k) and only
    #    k <= n / 2 is modelled, with weight 2 in the energy (weight 1 for k = n / 2);
    #  - the map i -> i + k splits the positions into cycles, and the sign changes along a
    #    cycle come in pairs, so the number of unequal pairs n - equal_k is even and equal_k
    #    has the same parity as n.
    energy = []
    for k in range(1, n // 2 + 1):
        weight = 1 if 2 * k == n else 2
        equal_pairs = [same[(min(i, (i + k) % n), max(i, (i + k) % n))] for i in range(n)]
        values = [v for v in range(n + 1) if (n - v) % 2 == 0]
        is_count = {v: f"correlation_{k}_has_{v}_equal_pairs" for v in values}
        for name in is_count.values():
            solver.addVariable(name, 0, 1)
        solver.addConstraint([(1, name) for name in is_count.values()], True, 1, True, 1)
        solver.addConstraint([(1, name) for name in equal_pairs]
                             + [(-v, name) for v, name in is_count.items() if v], True, 0, True, 0)
        energy += [(weight * (2 * v - n) ** 2, name) for v, name in is_count.items() if 2 * v != n]

    # minimise the sum of the squared autocorrelations
    return solver, {"sequence": sequence}, ("minimize", energy)
