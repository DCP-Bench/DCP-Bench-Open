"""Dudeney numbers: find a number larger than 1 with at most n digits that is a perfect cube whose
cube root equals the sum of its digits.

The model reports the number.
"""
from docplex.mp.model import Model


def build(instance):
    n = instance["n"]  # maximum number of digits
    top = 10 ** n - 1  # largest number with n digits

    model = Model("dudeney_numbers")

    # digit[i] is the i-th digit of the number, most significant first.
    digit = [model.integer_var(0, 9, name=f"digit_{i}") for i in range(n)]
    number = model.integer_var(0, top, name="number")

    # The number is written by its digits.
    model.add_constraint(number == model.sum(digit[i] * 10 ** (n - i - 1) for i in range(n)))

    # The cube root lies in 1..9n (the reference's domain: at most the largest digit sum).
    # number = root^3 multiplies variables, which CPLEX refuses, so the root is chosen one-hot
    # among the values whose cube still has at most n digits.
    roots = [r for r in range(1, 9 * n + 1) if r ** 3 <= top]
    is_root = {r: model.binary_var(name=f"is_root_{r}") for r in roots}
    model.add_constraint(model.sum(is_root.values()) == 1)
    cube_root = model.sum(r * is_root[r] for r in roots)

    # The number is the cube of its cube root.
    model.add_constraint(number == model.sum(r ** 3 * is_root[r] for r in roots))

    # The cube root equals the sum of the digits.
    model.add_constraint(cube_root == model.sum(digit))

    # The number is larger than 1.
    model.add_constraint(number >= 2)

    return model, {"number": number}
