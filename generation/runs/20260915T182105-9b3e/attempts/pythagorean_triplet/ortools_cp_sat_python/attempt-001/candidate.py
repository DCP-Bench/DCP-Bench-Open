from ortools.sat.python import cp_model


def build(instance):
    """Pythagorean triplet: the one whose three members sum to 1000.

    The puzzle states its own total, so `instance` is unused.
    """
    del instance

    model = cp_model.CpModel()
    a = model.new_int_var(1, 500, "a")
    b = model.new_int_var(1, 500, "b")
    c = model.new_int_var(1, 500, "c")

    model.add(a + b + c == 1000)

    aa = model.new_int_var(1, 500 * 500, "aa")
    bb = model.new_int_var(1, 500 * 500, "bb")
    cc = model.new_int_var(1, 500 * 500, "cc")
    model.add_multiplication_equality(aa, [a, a])
    model.add_multiplication_equality(bb, [b, b])
    model.add_multiplication_equality(cc, [c, c])
    model.add(aa + bb == cc)

    return model, {"a": a, "b": b, "c": c}
