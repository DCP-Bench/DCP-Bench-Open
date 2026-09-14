from ortools.sat.python import cp_model


def build(instance):
    n = instance["n"]
    half = n // 2
    model = cp_model.CpModel()
    x = [model.new_int_var(1, n, f"x_{i}") for i in range(half)]
    y = [model.new_int_var(1, n, f"y_{i}") for i in range(half)]
    model.add_all_different(x + y)
    model.add(sum(x) == sum(y))
    squares = []
    for name, values in (("x", x), ("y", y)):
        row = []
        for i, value in enumerate(values):
            square = model.new_int_var(1, n * n, f"square_{name}_{i}")
            model.add_multiplication_equality(square, [value, value])
            row.append(square)
        squares.append(row)
    model.add(sum(squares[0]) == sum(squares[1]))
    return model, {"A": x, "B": y}
