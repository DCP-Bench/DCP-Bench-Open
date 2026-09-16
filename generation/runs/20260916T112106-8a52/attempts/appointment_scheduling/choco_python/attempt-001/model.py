from pychoco.model import Model


def build(instance):
    """Appointment scheduling: give every person exactly one slot, every slot
    exactly one person, and only where the free-busy matrix allows it.
    """
    m = instance["m"]
    n = len(m)

    model = Model()
    x = [[model.boolvar(name=f"x{i}_{j}") for j in range(n)] for i in range(n)]

    for i in range(n):
        # The slot person i takes must be one they are free for.
        model.scalar(x[i], m[i], "=", 1).post()
        # One slot per person, and one person per slot.
        model.sum(x[i], "=", 1).post()
        model.sum([x[j][i] for j in range(n)], "=", 1).post()

    return model, {"x": x}
