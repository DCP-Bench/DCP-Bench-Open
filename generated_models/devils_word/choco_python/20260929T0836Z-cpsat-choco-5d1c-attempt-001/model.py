# Devil's word: put a plus or minus sign in front of every number of a list so
# that the signed numbers add up to the given total.
from pychoco.model import Model


def build(instance):
    arr = instance["arr"]  # the numbers, in order
    total = instance["total"]  # the sum the signed numbers must reach

    model = Model()

    # result[i] = arr[i] with its chosen sign: a variable over the two values
    # +arr[i] and -arr[i] (just 0 when the number is 0)
    result = []
    for i, value in enumerate(arr):
        if value == 0:
            result.append(model.intvar(0, 0, name=f"result_{i}"))
        else:
            result.append(model.intvar([-abs(value), abs(value)], name=f"result_{i}"))

    # the signed numbers add up to the total
    model.sum(result, "=", total).post()

    return model, {"result": result}
