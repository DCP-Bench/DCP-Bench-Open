from paramita.modelling import Bool, Iff

# Fibonacci even: the sequence 1, 2, 3, 5, 8, ... (each new term is the sum of the
# previous two); the answer is the sum of its even-valued terms that do not
# exceed four million. The instance has no fields; the problem fixes the bound.

BITS = 22  # every term up to the 32nd (3524578) fits in 22 bits
LIMIT = 4_000_000  # problem bound: "do not exceed four million"
N = 32  # horizon: F_33 = 5702887 > LIMIT, and the terms grow from the third term on,
        # so the first 32 terms contain every term that does not exceed LIMIT


def build(instance):
    # each term t_i is a binary integer: sum of 2**k * bit[i][k]
    t = [[Bool(f"t_{i}_{k}") for k in range(BITS)] for i in range(N)]

    def val(i):
        return sum(2**k * t[i][k] for k in range(BITS))

    cons = []
    # the sequence starts with 1 and 2
    cons.append(val(0) == 1)
    cons.append(val(1) == 2)
    # each new term is the sum of the previous two terms
    for i in range(N - 2):
        cons.append(val(i + 2) == val(i) + val(i + 1))

    # a term is even when its lowest bit is 0; an even term contributes its
    # higher bits: g[i][k] <-> bit k of term i is set and term i is even
    contributions = []
    for i in range(N):
        for k in range(1, BITS):
            g = Bool(f"even_{i}_{k}")
            cons.append(Iff(g, t[i][k] & ~t[i][0]))
            contributions.append(2**k * g)

    # res: the sum of the even-valued terms (all of them are within the bound,
    # because the horizon covers exactly the terms that do not exceed LIMIT)
    res = sum(contributions)

    return cons, {"res": res}
