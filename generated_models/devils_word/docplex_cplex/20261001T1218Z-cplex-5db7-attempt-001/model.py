"""Devil's word: give each number of a list (the character codes of a name) a plus or a minus
sign so that the signed numbers add up to the target total (666).

The model reports each number with its sign.
"""
from docplex.mp.model import Model


def build(instance):
    arr = instance["arr"]      # the numbers to sign
    total = instance["total"]  # the sum the signed numbers must reach
    n = len(arr)

    model = Model("devils_word")

    # plus[i] is 1 when arr[i] is added and 0 when it is subtracted: each number is either
    # added or subtracted.
    plus = [model.binary_var(name=f"plus_{i}") for i in range(n)]

    # result[i] is the number with its sign: arr[i] when added, -arr[i] when subtracted.
    result = [arr[i] * plus[i] - arr[i] * (1 - plus[i]) for i in range(n)]

    # The signed numbers add up to the total.
    model.add_constraint(model.sum(result) == total)

    return model, {"result": result}
