from ortools.sat.python import cp_model


def build(instance):
    """Hardy's 1729 square: four distinct numbers in 1..100 with
    a^2 + b^2 = c^2 + d^2.

    The puzzle states its own range, so `instance` is unused.
    """
    del instance

    range_min, range_max = 1, 100
    model = cp_model.CpModel()
    numbers = [model.new_int_var(range_min, range_max, name) for name in "abcd"]
    a, b, c, d = numbers

    squares = []
    for value, name in zip(numbers, "abcd"):
        square = model.new_int_var(range_min, range_max ** 2, f"{name}_squared")
        model.add_multiplication_equality(square, [value, value])
        squares.append(square)

    model.add(squares[0] + squares[1] == squares[2] + squares[3])
    model.add_all_different(numbers)

    return model, {"a": a, "b": b, "c": c, "d": d}
