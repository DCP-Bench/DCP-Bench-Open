"""ISBN-13: fill in the unknown digits so that the number starts with 978 or 979 and its check digit is right."""
import gurobipy as gp
from gurobipy import GRB

# An ISBN-13 has 13 digits; the first 12 are weighted 1, 3, 1, 3, ...
LENGTH = 13
WEIGHTS = [1 if i % 2 == 0 else 3 for i in range(LENGTH - 1)]


def build(instance):
    known = instance["isbn_init"]  # a digit, or -1 where it is unknown

    model = gp.Model("isbn")

    # isbn[i] is the i-th digit.
    isbn = model.addVars(LENGTH, lb=0, ub=9, vtype=GRB.INTEGER, name="isbn")

    # The known digits keep their values.
    for i in range(LENGTH):
        if known[i] != -1:
            model.addConstr(isbn[i] == known[i], name=f"known[{i}]")

    # The number starts with 978 or 979.
    model.addConstr(isbn[0] == 9, name="prefix0")
    model.addConstr(isbn[1] == 7, name="prefix1")
    model.addConstr(isbn[2] >= 8, name="prefix2")

    # The check digit is (10 - (sum % 10)) % 10 of the weighted sum of the first
    # 12 digits. Because it is a single digit, that is the same as saying the
    # weighted sum plus the check digit is a multiple of 10, which is linear.
    tens = model.addVar(lb=0, ub=(9 * sum(WEIGHTS) + 9) // 10, vtype=GRB.INTEGER, name="tens")
    model.addConstr(gp.quicksum(WEIGHTS[i] * isbn[i] for i in range(LENGTH - 1)) + isbn[LENGTH - 1]
                    == 10 * tens, name="check_digit")

    return model, {"isbn": [isbn[i] for i in range(LENGTH)]}
