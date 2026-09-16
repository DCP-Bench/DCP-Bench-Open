from pychoco.model import Model


def build(instance):
    """Three sum: pick exactly m of the numbers so that they add up to zero."""
    nums = instance["nums"]
    m = instance["m"]
    n = len(nums)

    model = Model()
    indices = [model.boolvar(name=f"i{i}") for i in range(n)]

    model.scalar(indices, nums, "=", 0).post()
    model.sum(indices, "=", m).post()

    return model, {"indices": indices}
