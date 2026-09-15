import cpmpy as cp


def build(instance):
    """Divisible by 1 through 9: a ten-digit pandigital number whose first n
    digits form a multiple of n, for every n.

    The puzzle fixes its own ten digits, so `instance` is unused.
    """
    del instance

    digits = 10
    x = cp.intvar(0, 9, shape=digits, name="x")
    # t[i] is the number formed by the first i + 1 digits.
    t = cp.intvar(0, 10 ** digits, shape=digits, name="t")
    number = t[digits - 1]

    model = cp.Model(cp.AllDifferent(x))
    for i in range(digits):
        prefix = cp.sum([x[j] * (10 ** (i - j)) for j in range(i + 1)])
        model += t[i] == prefix
        model += t[i] % (i + 1) == 0

    return model, {"number": number}
