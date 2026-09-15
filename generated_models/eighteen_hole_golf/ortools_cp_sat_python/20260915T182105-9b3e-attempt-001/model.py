from ortools.sat.python import cp_model


def build(instance):
    """Eighteen hole golf: eighteen holes of length three, four or five that
    add up to a par of seventy-two.

    The puzzle states its own course, so `instance` is unused.
    """
    del instance

    num_holes = 18
    total_length = 72

    model = cp_model.CpModel()
    holes = [model.new_int_var(3, 5, f"hole{i}") for i in range(num_holes)]

    model.add(sum(holes) == total_length)

    return model, {"holes": holes}
