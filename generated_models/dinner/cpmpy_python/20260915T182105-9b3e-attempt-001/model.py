import cpmpy as cp


def build(instance):
    """Dinner: twenty people for twenty dollars.

    The puzzle states its own party sizes and prices, so `instance` is unused.
    Prices are doubled through so the fifty-cent child stays an integer.
    """
    del instance

    grandparents = cp.intvar(1, 6, name="grandparents")
    parents = cp.intvar(1, 10, name="parents")
    children = cp.intvar(1, 40, name="children")

    model = cp.Model(
        grandparents * 6 + parents * 4 + children * 1 == 20 * 2,
        grandparents + parents + children == 20,
    )

    return model, {
        "grandparents": grandparents,
        "parents": parents,
        "children": children,
    }
