# Devil's word: put a plus or minus sign in front of every number of a list so
# that the signed numbers add up to the given total.
from hermax.model import Model


def build(instance):
    arr = instance["arr"]  # the numbers, in order
    total = instance["total"]  # the sum the signed numbers must reach
    n = len(arr)

    m = Model()
    # plus[i] is true when arr[i] is added and false when it is subtracted
    plus = m.bool_vector("plus", n)
    # result[i] = arr[i] with its chosen sign
    result = [m.int(f"result_{i}", -abs(arr[i]), abs(arr[i])) for i in range(n)]
    for i in range(n):
        m &= (~plus[i] | (result[i] == arr[i]))
        m &= (plus[i] | (result[i] == -arr[i]))

    # The signed numbers add up to the total. Writing it over the sign
    # Booleans, sum(arr) - 2 * (what is subtracted) = total, keeps the sum a
    # pseudo-Boolean constraint instead of a sum of integer variables.
    m &= (2 * sum(arr[i] * plus[i] for i in range(n)) == total + sum(arr))

    return m, {"result": result}
