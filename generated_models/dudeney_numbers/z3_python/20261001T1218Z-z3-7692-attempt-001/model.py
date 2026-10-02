# Dudeney number: a positive integer larger than 1 that is a perfect cube whose digits add up
# to its cube root. Find one with at most n digits.
import z3


def build(instance):
    n = instance["n"]  # maximum number of digits

    # number_digits[i] is the i-th digit of the number, most significant first, padded with
    # zeros on the left to n digits.
    number_digits = [z3.Int(f"number_digits_{i}") for i in range(n)]
    number = z3.Int("number")
    # The cube root is at least 1 and at most 9 * n (the digit sum is at most 9 per digit).
    cube_root = z3.Int("cube_root")

    solver = z3.Solver()

    for d in number_digits:
        solver.add(d >= 0, d <= 9)
    solver.add(number >= 0, number <= 10 ** n - 1)
    solver.add(cube_root >= 1, cube_root <= 9 * n)

    # The number is the cube of its cube root.
    solver.add(number == cube_root * cube_root * cube_root)

    # The digits add up to the cube root.
    solver.add(cube_root == z3.Sum(number_digits))

    # The digits are those of the number.
    solver.add(number == z3.Sum([number_digits[i] * 10 ** (n - i - 1) for i in range(n)]))

    # The number is larger than 1.
    solver.add(number > 1)

    return solver, {"number": number}
