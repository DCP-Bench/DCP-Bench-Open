# Dudeney numbers: a Dudeney number is a positive integer that is a perfect cube whose digit
# sum equals its cube root. Find one (with at most n digits) that is larger than 1.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]  # maximum number of digits

    pool = IDPool()
    # number_digits[i] = the i-th digit of the number, most significant first (leading zeros allowed)
    number_digits = [Integer(f"digit{i}", 0, 9, vpool=pool) for i in range(n)]
    # cube_root = the cube root of the number. It equals the digit sum, which is at most 9 * n.
    cube_root = Integer("cube_root", 1, 9 * n, vpool=pool)
    # number = the number itself. It has at most n digits, and it is the cube of a cube root of at
    # most 9 * n, which gives the upper bound. The runner blocks an answer by "number == value", so
    # the number needs a literal per value: the coupled encoding provides both kinds of literal.
    number = Integer("number", 0, min(10 ** n - 1, (9 * n) ** 3), encoding="coupled", vpool=pool)

    engine = IntegerEngine(vars=number_digits + [cube_root, number], vpool=pool)

    # the cube root equals the sum of the digits of the number
    engine.add_linear(cube_root == sum(number_digits))

    cnf = engine.clausify()

    # number == cube_root^3 and number == sum of digit * 10^position. PySAT has no product of two
    # variables, so the cube is tabulated over the domain of cube_root: choosing a cube root fixes
    # the number, and the number's digits are the digits of that cube.
    for root in range(1, 9 * n + 1):
        cube = root ** 3
        if cube >= 10 ** n:
            # a cube that does not fit in n digits cannot be the number
            cnf.append([-cube_root.equals(root)])
            continue
        cnf.append([-cube_root.equals(root), number.equals(cube)])
        for i, digit in enumerate(str(cube).zfill(n)):
            cnf.append([-cube_root.equals(root), number_digits[i].equals(int(digit))])

    # the number is larger than 1
    cnf.append([number.ge(2)])

    return cnf, {"number": number}
