from ortools.sat.python import cp_model


def build(instance):
    """Curious number: one more than it is a square, and one more than its
    half is a square too - and it is not 48, which is the known example.

    The puzzle fixes its own range, so `instance` is unused.
    """
    del instance

    model = cp_model.CpModel()
    peculiar = model.new_int_var(1, 10000, "peculiar")
    a = model.new_int_var(1, 10000, "a")
    b = model.new_int_var(1, 10000, "b")
    c = model.new_int_var(1, 10000, "c")
    d = model.new_int_var(1, 10000, "d")
    e = model.new_int_var(1, 10000, "e")

    model.add(peculiar != 48)
    # Add one and you get a square.
    model.add(peculiar + 1 == a)
    model.add_multiplication_equality(a, [b, b])
    # Halve it, add one, and you get a square again.
    model.add(peculiar == 2 * c)
    model.add(c + 1 == d)
    model.add_multiplication_equality(d, [e, e])

    return model, {"peculiar": peculiar}
