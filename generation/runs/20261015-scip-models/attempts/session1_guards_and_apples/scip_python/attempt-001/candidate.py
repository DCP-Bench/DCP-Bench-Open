# Guards and apples: the boy gives each of num_gates guards half of his apples plus one,
# as a whole number of apples, and the one apple left goes to the girl.
from pyscipopt import Model


def build(instance):
    n = instance["num_gates"]
    m = Model()

    # a[i] = number of apples before gate i (i = 0..n); a[n] is what is left after the last gate
    # Each gate doubles the count and adds 2 going backwards, so a[0] = 3 * 2**n - 2 and fits the bound.
    a = [m.addVar(name=f"apples_{i}", vtype="I", lb=0, ub=2 ** (n + 2)) for i in range(n + 1)]

    # h[i] = half of the apples before gate i; the boy has no knife, so this is a whole number
    h = [m.addVar(name=f"half_{i}", vtype="I", lb=0, ub=2 ** (n + 1)) for i in range(n)]

    # the apples before each gate are twice their half, so they are even
    for i in range(n):
        m.addCons(a[i] == 2 * h[i], name=f"even_before_gate_{i}")

    # the bribe at gate i is half of his apples plus one, h[i] + 1, which leaves h[i] - 1
    for i in range(n):
        m.addCons(a[i + 1] == h[i] - 1, name=f"left_after_gate_{i}")

    # after the last gate he has exactly one apple left, which he gives to the girl
    m.addCons(a[n] == 1, name="one_apple_for_girl")

    # number of apples before each gate, plus the number left after the last gate
    return m, {"apples": a}
