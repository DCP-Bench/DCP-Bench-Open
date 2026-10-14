"""A ten-digit number using each digit 0-9 once, whose first n digits are divisible by n for every n."""
import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data: ten digits, each of 0..9 used once.
LENGTH = 10
DIGITS = range(10)


def build(instance):
    model = gp.Model("divisible_by_1_through_9")

    # is_[i, d] = 1 when the i-th digit from the left is d; x[i] reads it back.
    is_ = model.addVars(LENGTH, DIGITS, vtype=GRB.BINARY, name="is")
    x = [model.addVar(lb=0, ub=9, vtype=GRB.INTEGER, name=f"x[{i}]") for i in range(LENGTH)]
    for i in range(LENGTH):
        model.addConstr(is_.sum(i, "*") == 1, name=f"one_digit[{i}]")
        model.addConstr(x[i] == gp.quicksum(d * is_[i, d] for d in DIGITS), name=f"read[{i}]")

    # Each of the digits 0 to 9 is used exactly once.
    for d in DIGITS:
        model.addConstr(is_.sum("*", d) == 1, name=f"used_once[{d}]")

    # The number formed by the first n digits is divisible by n. Written with
    # the place values 10^k the prefixes reach 10^10, where an integrality
    # tolerance of 1e-5 on one digit already moves the value by 10^4. Since
    # only the remainder matters, each place value is reduced modulo n first,
    # which keeps every coefficient below 10 and the check exact.
    for i in range(LENGTH):
        n = i + 1
        residue = gp.quicksum((10 ** (i - j)) % n * x[j] for j in range(i + 1))
        upper = sum((10 ** (i - j)) % n for j in range(i + 1)) * 9 // n
        quotient = model.addVar(lb=0, ub=upper, vtype=GRB.INTEGER, name=f"quotient[{n}]")
        model.addConstr(residue == n * quotient, name=f"divisible_by[{n}]")

    # The number itself, read from the rounded digits.
    number = gp.quicksum(10 ** (LENGTH - 1 - j) * x[j] for j in range(LENGTH))

    return model, {"number": number}
