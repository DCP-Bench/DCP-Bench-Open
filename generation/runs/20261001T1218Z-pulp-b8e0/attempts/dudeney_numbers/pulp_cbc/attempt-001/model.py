"""Dudeney numbers: a positive integer of at most n digits that is a perfect cube whose
digit sum equals its cube root, and that is larger than 1.

The model reports the number.
"""
import pulp


def build(instance):
    n = instance["n"]  # the maximum number of digits
    largest_root = 9 * n  # a digit sum of n digits is at most 9 * n, as in the reference

    problem = pulp.LpProblem("dudeney_numbers", pulp.LpMinimize)  # satisfaction

    # the digits of the number, most significant first (leading zeros allowed)
    digits = [pulp.LpVariable(f"digit_{i}", 0, 9, cat="Integer") for i in range(n)]
    number = pulp.LpVariable("number", 0, 10 ** n - 1, cat="Integer")

    # root[r] = 1 if the cube root of the number is r. Cubing is not linear, so the
    # root is chosen from its finite range and the cube is read from a table.
    root = {r: pulp.LpVariable(f"root_{r}", cat="Binary") for r in range(1, largest_root + 1)}
    problem += pulp.lpSum(root.values()) == 1

    # the number is a perfect cube: number = root * root * root
    problem += number == pulp.lpSum(r ** 3 * var for r, var in root.items())

    # the cube root equals the sum of the digits
    problem += pulp.lpSum(r * var for r, var in root.items()) == pulp.lpSum(digits)

    # the digits spell out the number
    problem += number == pulp.lpSum(digits[i] * 10 ** (n - i - 1) for i in range(n))

    # the number is larger than 1
    problem += number >= 2

    return problem, {"number": number}
