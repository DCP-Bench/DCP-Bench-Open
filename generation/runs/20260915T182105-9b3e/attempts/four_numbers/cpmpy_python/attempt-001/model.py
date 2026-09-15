import cpmpy as cp


def build(instance):
    """Four numbers: find three values whose subsets sum to every given number.
    """
    numbers = instance["numbers"]
    m = len(numbers)
    n = 3

    x = cp.intvar(1, 10, shape=n, name="x")
    # tmp[i, j] says whether x[j] is part of the subset that makes numbers[i].
    tmp = cp.boolvar(shape=(m, n), name="tmp")

    model = cp.Model()
    for i in range(m):
        model += cp.sum([tmp[i, j] * x[j] for j in range(n)]) == numbers[i]

    return model, {"x": x}
