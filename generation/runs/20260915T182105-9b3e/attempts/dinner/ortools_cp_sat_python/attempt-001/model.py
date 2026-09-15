from ortools.sat.python import cp_model


def build(instance):
    """Dinner: twenty people for twenty dollars.

    The puzzle states its own party sizes and prices, so `instance` is unused.
    Prices are doubled through so the fifty-cent child stays an integer.
    """
    del instance

    model = cp_model.CpModel()
    grandparents = model.new_int_var(1, 6, "grandparents")
    parents = model.new_int_var(1, 10, "parents")
    children = model.new_int_var(1, 40, "children")

    model.add(grandparents * 6 + parents * 4 + children * 1 == 20 * 2)
    model.add(grandparents + parents + children == 20)

    return model, {
        "grandparents": grandparents,
        "parents": parents,
        "children": children,
    }
