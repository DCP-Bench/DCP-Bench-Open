from ortools.sat.python import cp_model


def build(instance):
    """Dudeney numbers: a perfect cube whose digits sum to its cube root.
    """
    n = instance["n"]

    model = cp_model.CpModel()
    number_digits = [model.new_int_var(0, 9, f"d{i}") for i in range(n)]
    number = model.new_int_var(0, 10 ** n - 1, "number")
    cube_root = model.new_int_var(1, 9 * n, "cube_root")

    # The cube needs chaining: root squared, then times the root again.
    squared = model.new_int_var(1, (9 * n) ** 2, "squared")
    model.add_multiplication_equality(squared, [cube_root, cube_root])
    model.add_multiplication_equality(number, [squared, cube_root])

    model.add(cube_root == sum(number_digits))
    model.add(
        number == sum(number_digits[i] * (10 ** (n - i - 1)) for i in range(n))
    )
    model.add(number > 1)

    return model, {"number": number}
