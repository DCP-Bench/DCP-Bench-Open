from ortools.sat.python import cp_model


def build(instance):
    """Clock triplets: rearrange 1..12 around a clock face so that no three
    adjacent numbers sum above 21.

    The puzzle fixes the clock, so `instance` is unused.
    """
    del instance

    n = 12
    model = cp_model.CpModel()
    x = [model.new_int_var(1, n, f"x{i}") for i in range(n)]
    # The reference caps the largest triplet sum at 21 by declaring the
    # variable's domain rather than by optimizing.
    triplet_sum = model.new_int_var(0, 21, "triplet_sum")

    model.add_all_different(x)
    # Triplets wrap around the face, as the reference's negative indices do.
    for i in range(n):
        model.add(x[i] + x[(i - 1) % n] + x[(i - 2) % n] <= triplet_sum)

    return model, {"x": x}
