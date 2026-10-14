# Problem: sum the even-valued Fibonacci-style terms (1, 2, 3, 5, 8, ...) that do not exceed four million.
from pyscipopt import Model, quicksum

# Problem constants from the statement (not instance data): the limit on the terms,
# and the number of terms generated. Terms above the limit are excluded by the
# include flags below, so the length only has to be large enough to reach the limit.
# With terms 1, 2, 3, 5, ..., the 33rd term already exceeds 4,000,000, so 40 terms
# leave a wide margin.
LIMIT = 4_000_000
NUM_TERMS = 40
# Upper bound on every term: the 40th term is about 2.7e8, so every term stays below this.
TERM_UB = 300_000_000


def build(instance):
    m = Model()

    # f[k]: the k-th term, with its parity split off as f[k] = 2 * h[k] + p[k].
    f = [m.addVar(name=f"f_{k}", vtype="I", lb=0, ub=TERM_UB) for k in range(NUM_TERMS)]
    h = [m.addVar(name=f"h_{k}", vtype="I", lb=0, ub=TERM_UB // 2) for k in range(NUM_TERMS)]
    p = [m.addVar(name=f"odd_{k}", vtype="B") for k in range(NUM_TERMS)]
    # inc[k] = 1 if the term does not exceed the limit
    inc = [m.addVar(name=f"within_{k}", vtype="B") for k in range(NUM_TERMS)]
    # ev[k] = 1 if the term is even (the complement of odd)
    ev = [m.addVar(name=f"even_{k}", vtype="B") for k in range(NUM_TERMS)]
    # chosen[k] = 1 if the term is even and within the limit
    chosen = [m.addVar(name=f"chosen_{k}", vtype="B") for k in range(NUM_TERMS)]
    # t[k] = f[k] when chosen, else 0 (linearises the product chosen * f)
    t = [m.addVar(name=f"picked_{k}", vtype="I", lb=0, ub=TERM_UB) for k in range(NUM_TERMS)]

    # the sequence starts with 1 and 2
    m.addCons(f[0] == 1)
    m.addCons(f[1] == 2)
    # each new term is the sum of the previous two terms
    for k in range(2, NUM_TERMS):
        m.addCons(f[k] == f[k - 1] + f[k - 2])

    for k in range(NUM_TERMS):
        # parity: the term is 2 * h + p with p binary
        m.addCons(f[k] == 2 * h[k] + p[k])
        m.addCons(ev[k] + p[k] == 1)

        # the term is within the limit: an indicator selects the side of the bound
        m.addConsIndicator(f[k] <= LIMIT, binvar=inc[k])
        m.addConsIndicator(f[k] >= LIMIT + 1, binvar=inc[k], activeone=False)

        # chosen = within AND even
        m.addConsAnd([inc[k], ev[k]], chosen[k])

        # t[k] = f[k] if chosen[k] == 1, and 0 otherwise
        m.addCons(t[k] <= f[k])
        m.addCons(t[k] <= TERM_UB * chosen[k])
        m.addCons(t[k] >= f[k] - TERM_UB * (1 - chosen[k]))

    # the output: the sum of the even terms that do not exceed the limit
    res = m.addVar(name="res", vtype="I", lb=0, ub=4 * LIMIT)
    m.addCons(res == quicksum(t[k] for k in range(NUM_TERMS)))

    return m, {"res": res}
