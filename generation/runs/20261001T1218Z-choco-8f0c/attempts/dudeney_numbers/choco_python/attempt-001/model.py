# Dudeney numbers: find a positive integer larger than 1 with at most n digits that is a perfect
# cube whose digit sum equals its cube root.
from pychoco.model import Model


def build(instance):
    n = instance["n"]  # maximum number of digits
    top = 10 ** n - 1  # largest number with n digits

    model = Model()

    # number_digits[i] = the i-th decimal digit of the number, most significant first
    digits = [model.intvar(0, 9, name=f"digit_{i}") for i in range(n)]
    number = model.intvar(0, top, name="number", bounded_domain=True)
    # the cube root is the digit sum, so it lies in 1..9n
    cube_root = model.intvar(1, 9 * n, name="cube_root")

    # The digits spell the number.
    model.scalar(digits, [10 ** (n - i - 1) for i in range(n)], "=", number).post()

    # The cube root equals the sum of the digits.
    model.sum(digits, "=", cube_root).post()

    # The number is the cube of its cube root. Stated as a table of (root, cube) pairs whose cube
    # fits in n digits, rather than a chain of products.
    cubes = [(r, r ** 3) for r in range(1, 9 * n + 1) if r ** 3 <= top]
    model.table([cube_root, number], cubes).post()

    # The number is larger than 1.
    model.arithm(number, ">", 1).post()

    return model, {"number": number}
