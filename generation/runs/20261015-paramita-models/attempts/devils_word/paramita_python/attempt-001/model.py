"""Devil's word: insert '+' or '-' before each integer so that the signed sum is 666.

Each array position gets one Boolean: true means '+', false means '-'.
The signed value of position i is 2*a_i*plus_i - a_i, which is +a_i when plus_i
is true and -a_i otherwise. The output `result` lists these signed values.
"""

from paramita.modelling import Bool


def build(instance):
    arr = instance["arr"]
    total = instance["total"]
    n = len(arr)

    # one sign per position: plus[i] is true when the i-th integer gets '+'
    plus = [Bool(f"plus_{i}") for i in range(n)]

    # insert a + or - operator before each integer: its signed value is +arr[i] or -arr[i]
    result = [2 * arr[i] * plus[i] - arr[i] for i in range(n)]

    cons = []
    # summing them up will result in the total (666): the signed integers add up to total
    cons.append(sum(result) == total)

    return cons, {"result": result}
