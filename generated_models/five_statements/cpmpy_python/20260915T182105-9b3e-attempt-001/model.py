import cpmpy as cp


def build(instance):
    """Five self-referential statements, the i-th claiming that exactly i + 1
    of them are false.

    The puzzle states its own five claims, so `instance` is unused.
    """
    del instance

    n = 5
    statements = cp.boolvar(shape=n, name="statements")

    false_count = cp.sum([~statements[j] for j in range(n)])
    model = cp.Model(
        [statements[i] == (false_count == i + 1) for i in range(n)]
    )

    return model, {"statements": statements}
