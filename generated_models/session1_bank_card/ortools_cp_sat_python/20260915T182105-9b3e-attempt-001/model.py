from ortools.sat.python import cp_model


def build(instance):
    """Bank card: a four-digit PIN abcd where cd is three times ab and da is
    twice bc.

    The puzzle states its own rules, so `instance` is unused.
    """
    del instance

    model = cp_model.CpModel()
    a, b, c, d = [model.new_int_var(0, 9, name) for name in "abcd"]

    model.add_all_different([a, b, c, d])
    model.add(10 * c + d == 3 * (10 * a + b))
    model.add(10 * d + a == 2 * (10 * b + c))

    return model, {"a": a, "b": b, "c": c, "d": d}
