import cpmpy as cp


def build(instance):
    nums, wanted = instance["nums"], instance["m"]
    n = len(nums)
    indices = cp.boolvar(shape=n, name="indices")
    model = cp.Model(cp.sum([nums[i] * indices[i] for i in range(n)]) == 0,
                     cp.sum([indices[i] for i in range(n)]) == wanted)
    return model, {"indices": [indices[i] for i in range(n)]}
