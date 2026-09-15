import cpmpy as cp


def build(instance):
    """Dudeney numbers: a perfect cube whose digits sum to its cube root.
    """
    n = instance["n"]

    number_digits = cp.intvar(0, 9, shape=n, name="number_digits")
    number = cp.intvar(0, 10 ** n - 1, name="number")
    cube_root = cp.intvar(1, 9 * n, name="cube_root")

    model = cp.Model(
        number == cube_root * cube_root * cube_root,
        cube_root == cp.sum(number_digits),
        number == cp.sum(
            [number_digits[i] * (10 ** (n - i - 1)) for i in range(n)]
        ),
        number > 1,
    )

    return model, {"number": number}
