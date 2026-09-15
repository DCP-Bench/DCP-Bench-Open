import cpmpy as cp


def build(instance):
    given = instance["isbn_init"]
    n = len(given)
    isbn = cp.intvar(0, 9, shape=n, name="isbn")
    model = cp.Model()
    # A -1 in the instance marks the digit to find.
    for i in range(n):
        if given[i] != -1:
            model += isbn[i] == given[i]
    model += isbn[0] == 9
    model += isbn[1] == 7
    model += (isbn[2] == 8) | (isbn[2] == 9)
    check = cp.sum([isbn[i] * (1 if i % 2 == 0 else 3) for i in range(n - 1)])
    model += isbn[n - 1] == (10 - (check % 10)) % 10
    return model, {"isbn": [isbn[i] for i in range(n)]}
