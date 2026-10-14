# Best host: seat six guests round a table so that everyone sits only next to
# guests they get along with.
from hermax.model import Model

# prefs[g] = the guests g is willing to sit next to; 0 Andrew, 1 Betty, 2 Cara,
# 3 Dave, 4 Erica, 5 Frank
PREFS = [[3, 5], [2, 4], [1, 5], [0, 4], [1, 3], [0, 2]]


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    n = len(PREFS)
    m = Model()
    # x[i] = the guest at seat i, going round the table
    x = m.int_vector("x", n, 0, n - 1)

    # every guest gets one seat
    m &= m.vector([x[i] for i in range(n)]).all_different()

    # Two guests in neighbouring seats must each be willing to sit next to the other.
    compatible = [(a, b) for a in range(n) for b in PREFS[a] if a in PREFS[b]]
    for i in range(n):
        m &= m.vector([x[i], x[(i + 1) % n]]).is_in(compatible)

    return m, {"x": x}
