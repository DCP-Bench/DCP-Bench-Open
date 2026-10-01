# Devil's word: put a '+' or a '-' in front of every number of a list so that the signed
# numbers add up to the given total.
import cpmpy as cp


def build(instance):
    arr = instance["arr"]        # the numbers to be signed
    total = instance["total"]    # the sum the signed numbers must reach
    n = len(arr)
    max_val = max(arr)

    # plus[i] is true when arr[i] is added, false when it is subtracted.
    plus = cp.boolvar(shape=n, name="plus")
    # result[i] is arr[i] with its chosen sign.
    result = cp.intvar(-max_val, max_val, shape=n, name="result")

    model = cp.Model()

    # Each number is either added or subtracted.
    for i in range(n):
        model += result[i] == arr[i] * plus[i] - arr[i] * (1 - plus[i])

    # The signed numbers add up to the total.
    model += cp.sum(result) == total

    return model, {"result": result}
