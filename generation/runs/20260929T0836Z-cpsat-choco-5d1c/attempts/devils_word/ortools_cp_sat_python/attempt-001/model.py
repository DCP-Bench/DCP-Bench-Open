# Devil's word: put a plus or minus sign in front of every number of a list so
# that the signed numbers add up to the given total.
from ortools.sat.python import cp_model


def build(instance):
    arr = instance["arr"]  # the numbers, in order
    total = instance["total"]  # the sum the signed numbers must reach
    n = len(arr)
    max_val = max(arr)

    model = cp_model.CpModel()

    # plus[i] is true when arr[i] is added and false when it is subtracted
    plus = [model.new_bool_var(f"plus_{i}") for i in range(n)]
    # result[i] = arr[i] with its chosen sign
    result = [model.new_int_var(-max_val, max_val, f"result_{i}") for i in range(n)]

    # each number is added or subtracted (never both, never neither)
    for i in range(n):
        model.add(result[i] == arr[i]).only_enforce_if(plus[i])
        model.add(result[i] == -arr[i]).only_enforce_if(plus[i].negated())

    # the signed numbers add up to the total
    model.add(sum(result) == total)

    return model, {"result": result}
