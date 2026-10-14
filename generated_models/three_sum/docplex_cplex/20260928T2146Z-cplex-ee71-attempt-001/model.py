"""Zero sum: select exactly m of the numbers so that they add up to zero."""
from docplex.mp.model import Model


def build(instance):
    nums, m = instance["nums"], instance["m"]

    model = Model("three_sum")

    # indices[i] is 1 when nums[i] is selected.
    indices = model.binary_var_list(len(nums), name="indices")

    # The selected numbers add up to zero.
    model.add_constraint(model.dot(indices, nums) == 0, ctname="zero_sum")

    # Exactly m numbers are selected.
    model.add_constraint(model.sum(indices) == m, ctname="count")

    return model, {"indices": indices}
