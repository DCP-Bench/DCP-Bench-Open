from ortools.sat.python import cp_model


def build(instance):
    """Ages of the sons: the product is 36, the sum is ambiguous, and there is
    a unique oldest.

    The puzzle states its own product, so `instance` is unused.  The second
    triple B is what makes the sum ambiguous: it is a different factorisation
    of 36 with the same sum, which is why the mathematician needed the extra
    clue about the oldest son.
    """
    del instance

    model = cp_model.CpModel()
    a1 = model.new_int_var(0, 36, "A1")
    a2 = model.new_int_var(0, 36, "A2")
    a3 = model.new_int_var(0, 36, "A3")
    b1 = model.new_int_var(0, 36, "B1")
    b2 = model.new_int_var(0, 36, "B2")
    b3 = model.new_int_var(0, 36, "B3")

    # Triple products need chaining two factors at a time.
    a12 = model.new_int_var(0, 36 * 36, "a12")
    b12 = model.new_int_var(0, 36 * 36, "b12")
    model.add_multiplication_equality(a12, [a1, a2])
    model.add_multiplication_equality(b12, [b1, b2])

    model.add(a1 > a2)
    model.add(a2 >= a3)
    model.add_multiplication_equality(36, [a12, a3])

    model.add(b1 >= b2)
    model.add(b2 >= b3)
    model.add(a1 != b1)
    model.add_multiplication_equality(36, [b12, b3])

    a_sum = model.new_int_var(0, 1000, "AS")
    b_sum = model.new_int_var(0, 1000, "BS")
    model.add(a_sum == a1 + a2 + a3)
    model.add(b_sum == b1 + b2 + b3)
    model.add(a_sum == b_sum)

    return model, {"A1": a1, "A2": a2, "A3": a3}
