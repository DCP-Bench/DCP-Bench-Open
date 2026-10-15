# Number partitioning: split the numbers 1..N into two sets A and B of equal
# size, equal sum and equal sum of squares. N is read from the instance.
# Encoding: one-hot over slots. a[i][j] = number i is the j-th element of A,
# b[i][j] = number i is the j-th element of B. The output lists are the slots.
from paramita.modelling import Bool


def build(instance):
    n = instance["n"]
    h = n // 2
    nums = range(1, n + 1)
    a = {i: [Bool(f"a_{i}_{j}") for j in range(h)] for i in nums}
    b = {i: [Bool(f"b_{i}_{j}") for j in range(h)] for i in nums}
    cons = []

    # every number is in exactly one of A or B
    for i in nums:
        cons.append(sum(a[i]) + sum(b[i]) == 1)

    # every slot of A and of B holds exactly one number, so |A| = |B| = N/2
    for j in range(h):
        cons.append(sum(a[i][j] for i in nums) == 1)
        cons.append(sum(b[i][j] for i in nums) == 1)

    # A and B have the same sum of numbers
    cons.append(sum(i * a[i][j] for i in nums for j in range(h))
                == sum(i * b[i][j] for i in nums for j in range(h)))

    # A and B have the same sum of squares
    cons.append(sum(i * i * a[i][j] for i in nums for j in range(h))
                == sum(i * i * b[i][j] for i in nums for j in range(h)))

    # output slots are listed in increasing order (symmetry breaking on the output)
    slot_a = [sum(i * a[i][j] for i in nums) for j in range(h)]
    slot_b = [sum(i * b[i][j] for i in nums) for j in range(h)]
    for j in range(h - 1):
        cons.append(slot_a[j] + 1 <= slot_a[j + 1])
        cons.append(slot_b[j] + 1 <= slot_b[j + 1])

    return cons, {"A": slot_a, "B": slot_b}
