# Number partitioning (CSPLib 49): split the numbers 1..N into two sets A and B of equal size whose
# sums are equal and whose sums of squares are equal.
from pychoco.model import Model


def build(instance):
    n = instance["n"]  # the number N; the reference requires it to be even
    half = n // 2

    model = Model()

    # A[i] and B[i] are the i-th numbers of the two sets; equal cardinality is built in.
    a = [model.intvar(1, n, name=f"A_{i}") for i in range(half)]
    b = [model.intvar(1, n, name=f"B_{i}") for i in range(half)]

    # Every number 1..N is used once: the two sets together hold N distinct values.
    model.all_different(a + b).post()

    # The sum of the numbers in A equals the sum of the numbers in B.
    model.scalar(a + b, [1] * half + [-1] * half, "=", 0).post()

    # The sum of squares in A equals the sum of squares in B. Each square is an auxiliary
    # variable fixed by its number, bounded by N^2.
    a_sq = [model.intvar(1, n * n, name=f"A_sq_{i}") for i in range(half)]
    b_sq = [model.intvar(1, n * n, name=f"B_sq_{i}") for i in range(half)]
    for v, sq in zip(a + b, a_sq + b_sq):
        model.square(sq, v).post()
    model.scalar(a_sq + b_sq, [1] * half + [-1] * half, "=", 0).post()

    return model, {"A": a, "B": b}
