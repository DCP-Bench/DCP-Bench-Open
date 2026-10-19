# Devil's word: insert a '+' or '-' before each integer of the array so that the
# signed integers sum to the total. The output is the array with the signs applied.
import mip


def build(instance):
    arr = instance["arr"]
    total = instance["total"]
    n = len(arr)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # sign[i] = 1 when a '+' is put before integer i, 0 when a '-' is put there
    sign = [model.add_var(f"sign_{i}", var_type=mip.BINARY) for i in range(n)]
    # result[i] is integer i with its sign; its bounds come from the integer itself
    result = [
        model.add_var(f"result_{i}", lb=-abs(arr[i]), ub=abs(arr[i]), var_type=mip.INTEGER)
        for i in range(n)
    ]

    # each integer carries exactly one sign: result is +arr[i] when sign is 1, -arr[i] when it is 0
    for i in range(n):
        model.add_constr(result[i] == 2 * arr[i] * sign[i] - arr[i], f"sign_{i}")

    # the signed integers add up to the total
    model.add_constr(mip.xsum(result) == total, "total")

    return model, {"result": result}
