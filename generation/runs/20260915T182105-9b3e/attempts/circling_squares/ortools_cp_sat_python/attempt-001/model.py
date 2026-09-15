from ortools.sat.python import cp_model


def build(instance):
    """Circling the squares: ten different numbers around a circle where any
    two adjacent squares sum to the same as the two diametrically opposite.

    The puzzle states its own four given numbers, so `instance` is unused.
    """
    del instance

    n = 10
    model = cp_model.CpModel()
    names = "ABCDEFGHIK"
    x = [model.new_int_var(1, 99, name) for name in names]
    a, b, c, d, e, f, g, h, i, k = x

    model.add_all_different(x)
    # The four numbers given as examples.
    model.add(a == 16)
    model.add(b == 2)
    model.add(f == 8)
    model.add(g == 14)

    # One squared variable per position, reused across the five equations.
    squares = {}
    for value, name in zip(x, names):
        square = model.new_int_var(1, 99 * 99, f"{name}_squared")
        model.add_multiplication_equality(square, [value, value])
        squares[name] = square

    for first, second, third, fourth in (
        ("A", "B", "F", "G"),
        ("B", "C", "G", "H"),
        ("C", "D", "H", "I"),
        ("D", "E", "I", "K"),
        ("E", "F", "K", "A"),
    ):
        model.add(
            squares[first] + squares[second] == squares[third] + squares[fourth]
        )

    return model, {name: var for name, var in zip(names, x)}
