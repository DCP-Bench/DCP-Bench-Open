from ortools.sat.python import cp_model


def build(instance):
    nums, wanted = instance["nums"], instance["m"]
    n = len(nums)
    model = cp_model.CpModel()
    indices = [model.new_bool_var(f"i_{i}") for i in range(n)]
    model.add(sum(nums[i] * indices[i] for i in range(n)) == 0)
    model.add(sum(indices) == wanted)
    return model, {"indices": indices}
