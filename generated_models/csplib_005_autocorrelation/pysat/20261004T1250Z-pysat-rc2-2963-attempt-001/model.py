# Low autocorrelation binary sequences (CSPLib 5), periodic version: choose a
# +1/-1 sequence of length n minimising the sum over k = 1..n-1 of the
# squared periodic autocorrelation C_k = sum_i S_i * S_{(i+k) mod n}.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def build(instance):
    n = instance["n"]
    shifts = range(1, n // 2 + 1)

    pool = IDPool()
    # sequence[i] is the bit at position i, -1..1 as in the reference.
    # Direct encoding: a value literal per bit value.
    sequence = [Integer(f"sequence_{i}", -1, 1, vpool=pool) for i in range(n)]
    # count[k] is D_k, the number of positions i whose bit differs from the
    # bit k places on (cyclically), 0..n. Order encoding: D_k >= v is one
    # literal, which the objective charges.
    count = {k: Integer(f"differ_count_{k}", 0, n, encoding="order", vpool=pool)
             for k in shifts}
    engine = IntegerEngine(vars=sequence + list(count.values()), vpool=pool)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # Each bit is +1 or -1, never 0.
    for s in sequence:
        formula.append([-s.equals(0)])
    plus = [s.equals(1) for s in sequence]

    # S_i * S_j is -1 exactly when the bits differ, so C_k = n - 2 * D_k.
    # Periodic shifts k and n - k compare the same pairs, so C_k = C_{n-k}
    # and only k = 1..n//2 is built, counted twice unless k = n - k.
    for k in shifts:
        times = 1 if 2 * k == n else 2
        differ = []
        for i in range(n):
            j = (i + k) % n
            d = pool.id(("differ", k, i))
            # d is true exactly when bits i and j differ.
            formula.append([-d, plus[i], plus[j]])
            formula.append([-d, -plus[i], -plus[j]])
            formula.append([d, -plus[i], plus[j]])
            formula.append([d, plus[i], -plus[j]])
            differ.append(d)
        # D_k counts the differing positions.
        steps = [count[k].ge(v) for v in range(1, n + 1)]
        formula.extend(PBEnc.equals(lits=differ + steps,
                                    weights=[1] * n + [-1] * n, bound=0,
                                    vpool=pool).clauses)

        # Minimise E = sum C_k^2: shift k contributes times * (n - 2 D)^2.
        # Written as a sum over thresholds v of the change between D = v - 1
        # and D = v; a positive change is paid when D_k >= v holds, a negative
        # one (as its absolute value) when it fails. That adds a constant to
        # the true energy, which does not move the optimum.
        for v in range(1, n + 1):
            delta = times * ((n - 2 * v) ** 2 - (n - 2 * (v - 1)) ** 2)
            if delta > 0:
                formula.append([-count[k].ge(v)], weight=delta)
            elif delta < 0:
                formula.append([count[k].ge(v)], weight=-delta)

    return formula, {"sequence": sequence}
