# Dudeney numbers: a positive integer that is a perfect cube whose digits add up
# to its cube root. Find one larger than 1, with at most n digits.
from exact import Exact


def build(instance):
    n = instance["n"]  # most digits of the number

    solver = Exact()
    # digits[i] = the i-th digit of the number, counted from the left, with leading zeros
    digits = [f"digit_{i}" for i in range(n)]
    for name in digits:
        solver.addVariable(name, 0, 9)
    # number is at most n digits long, and larger than 1; cube_root is at least 1 and,
    # the digits being at most 9 each, at most 9n
    solver.addVariable("number", 2, 10 ** n - 1)
    solver.addVariable("cube_root", 1, 9 * n)
    solver.addVariable("square", 1, (9 * n) ** 2)

    # number = cube_root ** 3
    solver.addMultiplication(["cube_root", "cube_root"], True, "square", True, "square")
    solver.addMultiplication(["square", "cube_root"], True, "number", True, "number")
    # the digits add up to the cube root
    solver.addConstraint([(1, name) for name in digits] + [(-1, "cube_root")], True, 0, True, 0)
    # the digits spell the number
    solver.addConstraint([(10 ** (n - 1 - i), digits[i]) for i in range(n)] + [(-1, "number")],
                         True, 0, True, 0)

    return solver, {"number": "number"}
