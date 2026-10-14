"""Dudeney numbers: a perfect cube larger than 1, of at most n digits, whose digit sum equals its cube root."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]     # maximum number of digits
    roots = range(1, 9 * n + 1)   # the digit sum of n digits is at most 9n, as in the reference

    model = gp.Model("dudeney_numbers")
    # Coefficients reach 10^(n-1) and (9n)^3, so a binary off by the default
    # integrality tolerance could move the number by more than 1; tighten it.
    model.Params.IntFeasTol = 1e-9

    # The n digits of the number, most significant first, and the number itself.
    digits = model.addVars(n, lb=0, ub=9, vtype=GRB.INTEGER, name="digits")
    number = model.addVar(lb=0, ub=10 ** n - 1, vtype=GRB.INTEGER, name="number")

    # is_root[r] is 1 when the cube root is r; this keeps number = root^3 linear.
    is_root = model.addVars(roots, vtype=GRB.BINARY, name="is_root")
    model.addConstr(is_root.sum() == 1, name="one_root")
    cube_root = gp.quicksum(r * is_root[r] for r in roots)

    # The number is the cube of its cube root.
    model.addConstr(number == gp.quicksum(r ** 3 * is_root[r] for r in roots), name="cube")

    # The cube root equals the sum of the digits.
    model.addConstr(cube_root == digits.sum(), name="digit_sum")

    # The number is written by its digits.
    model.addConstr(number == gp.quicksum(digits[i] * 10 ** (n - i - 1) for i in range(n)), name="digits")

    # The number is larger than 1.
    model.addConstr(number >= 2, name="above_one")

    return model, {"number": number}
