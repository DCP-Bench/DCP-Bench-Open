from pychoco.model import Model


def build(instance):
    """Clock triplets: rearrange 1..12 around a clock face so that no three
    adjacent numbers sum above 21.
    """
    del instance

    n = 12
    model = Model()
    x = [model.intvar(1, n, name=f"x{i}") for i in range(n)]
    # The reference caps the largest triplet sum at 21 by declaring the
    # variable's domain rather than by optimizing.
    triplet_sum = model.intvar(0, 21, name="triplet_sum")

    model.all_different(x).post()
    # Triplets wrap around the face.
    for i in range(n):
        trio = [x[i], x[(i - 1) % n], x[(i - 2) % n], triplet_sum]
        model.scalar(trio, [1, 1, 1, -1], "<=", 0).post()

    return model, {"x": x}
