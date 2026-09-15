from ortools.sat.python import cp_model


def build(instance):
    """Five floors: put Baker, Cooper, Fletcher, Miller and Smith on five
    different floors under the stated restrictions.

    The puzzle states its own residents and clues, so `instance` is unused.
    """
    del instance

    model = cp_model.CpModel()
    baker = model.new_int_var(1, 5, "B")
    cooper = model.new_int_var(1, 5, "C")
    fletcher = model.new_int_var(1, 5, "F")
    miller = model.new_int_var(1, 5, "M")
    smith = model.new_int_var(1, 5, "S")

    model.add(baker != 5)
    model.add(cooper != 1)
    model.add(fletcher != 5)
    model.add(fletcher != 1)
    model.add(miller > cooper)

    # Neither Smith nor Cooper is next door to Fletcher.
    for first, second, label in ((smith, fletcher, "sf"), (fletcher, cooper, "fc")):
        gap = model.new_int_var(0, 4, f"gap_{label}")
        model.add_abs_equality(gap, first - second)
        model.add(gap != 1)

    model.add_all_different([baker, cooper, fletcher, miller, smith])

    return model, {
        "B": baker, "C": cooper, "F": fletcher, "M": miller, "S": smith,
    }
