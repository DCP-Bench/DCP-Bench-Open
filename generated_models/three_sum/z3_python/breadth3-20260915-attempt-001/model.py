import z3


def build(instance):
    nums, wanted = instance["nums"], instance["m"]
    n = len(nums)
    indices = [z3.Bool(f"i_{i}") for i in range(n)]
    picked = [z3.If(indices[i], 1, 0) for i in range(n)]
    constraints = [z3.Sum([nums[i] * picked[i] for i in range(n)]) == 0,
                   z3.Sum(picked) == wanted]
    return constraints, {"indices": indices}
