# Giant cat army riddle: build a list that starts with 0, where each next element is the previous
# one plus 5, plus 7, or its square root. All elements are distinct integers of at most 60, the list
# has 24 elements, it ends with 14, and 2 appears before 10 in it.
import cpmpy as cp


def build(instance):
    # The largest value and the list length belong to the problem statement (the instance has no
    # fields), so they are mirrored here.
    maxval = 60
    n = 24

    # x[i] = i-th element of the list
    x = cp.intvar(0, maxval, shape=(n,), name="x")

    model = cp.Model()

    # All elements are distinct.
    model += cp.AllDifferent(x)

    # The list starts with 0 and ends with 14.
    model += x[0] == 0
    model += x[n - 1] == 14

    # The second element is 5 or 7 (0 + 5 or 0 + 7; the square root of 0 would repeat 0).
    model += (x[1] == 5) | (x[1] == 7)

    # Each element comes from the previous one by adding 5, adding 7, or taking the square root
    # (the previous element is the square of the next one).
    for i in range(n - 1):
        model += ((x[i + 1] == x[i] + 5) |
                  (x[i + 1] == x[i] + 7) |
                  (x[i] == x[i + 1] * x[i + 1]))

    # The numbers 2, 10 and 14 appear in this order (14 is the last element already).
    # ix2, ix10 = positions of 2 and 10 in the list
    ix2 = cp.intvar(0, n - 1, name="ix2")
    ix10 = cp.intvar(0, n - 1, name="ix10")
    model += x[ix2] == 2
    model += x[ix10] == 10
    model += ix2 < ix10

    return model, {"x": x}
