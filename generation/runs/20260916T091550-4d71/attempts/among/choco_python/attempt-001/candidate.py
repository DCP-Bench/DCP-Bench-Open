from pychoco.model import Model


def build(instance):
    """Among: exactly m of the n entries of x must take a value drawn from v;
    the rest are free within the domain.
    """
    n = instance["n"]
    m = instance["m"]
    wanted = instance["v"]

    model = Model()
    # Domain 0..7 comes from the problem statement, which fixes it for every
    # instance; the reference declares the same range.
    x = [model.intvar(0, 7, name=f"x{i}") for i in range(n)]

    # Count the (position, wanted value) hits exactly as the reference does.
    hits = []
    for variable in x:
        for value in wanted:
            hits.append(model.arithm(variable, "=", value).reify())
    model.sum(hits, "=", m).post()

    return model, {"x": x}
