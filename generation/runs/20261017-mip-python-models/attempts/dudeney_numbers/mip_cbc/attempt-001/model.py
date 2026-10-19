# Dudeney numbers: a positive integer that is a perfect cube such that the sum
# of its digits equals the cube root of the number. Print such a number that is
# also larger than 1. The instance field n bounds the number of digits.
import mip


def build(instance):
    n = instance["n"]
    limit = 10 ** n - 1  # largest number with at most n digits

    # largest cube root k with k**3 <= limit, computed from the instance bound
    K = 1
    while (K + 1) ** 3 <= limit:
        K += 1

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # the cube root, chosen as one value out of 1..K
    choose = [model.add_var(f"c_{k}", var_type=mip.BINARY) for k in range(1, K + 1)]
    model += mip.xsum(choose) == 1
    root = model.add_var("root", lb=1, ub=K, var_type=mip.INTEGER)
    model += root == mip.xsum(k * choose[k - 1] for k in range(1, K + 1))

    # the number: a perfect cube, equal to root cubed
    number = model.add_var("number", lb=2, ub=limit, var_type=mip.INTEGER)
    model += number == mip.xsum(k ** 3 * choose[k - 1] for k in range(1, K + 1))

    # the digits of the number, each 0..9, at most n of them
    digits = [model.add_var(f"d_{i}", lb=0, ub=9, var_type=mip.INTEGER) for i in range(n)]
    model += number == mip.xsum(10 ** i * digits[i] for i in range(n))

    # the sum of the digits is equal to the cube root of the number
    model += mip.xsum(digits) == root

    return model, {"number": number}
