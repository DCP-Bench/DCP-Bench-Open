import cpmpy as cp


def build(instance):
    """Eighteen hole golf: eighteen holes of length three, four or five that
    add up to a par of seventy-two.

    The puzzle states its own course, so `instance` is unused.
    """
    del instance

    num_holes = 18
    total_length = 72

    holes = cp.intvar(3, 5, shape=num_holes, name="holes")

    model = cp.Model(cp.sum(holes) == total_length)

    return model, {"holes": holes}
