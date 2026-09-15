from ortools.sat.python import cp_model


def build(instance):
    """Bowls and oranges: place m oranges in n bowls spaced a metre apart so
    that no three of them are evenly spaced.
    """
    n = instance["n"]
    m = instance["m"]

    model = cp_model.CpModel()
    x = [model.new_int_var(1, n, f"x{i}") for i in range(m)]

    model.add_all_different(x)
    # Positions are reported in ascending order.
    for i in range(1, m):
        model.add(x[i - 1] <= x[i])
    # No three oranges A, B, C with B as far from A as C is from B.
    for i in range(m):
        for j in range(i + 1, m):
            for k in range(j + 1, m):
                model.add(x[j] - x[i] != x[k] - x[j])

    return model, {"x": x}
