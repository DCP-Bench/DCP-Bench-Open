"""Bank card PIN: four distinct digits abcd with cd = 3 * ab and da = 2 * bc."""
import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data.
NAMES = "abcd"
DIGITS = range(10)


def build(instance):
    model = gp.Model("session1_bank_card")

    # is_[x, v] = 1 when digit x of the PIN is v; pin[x] reads it back.
    is_ = model.addVars(NAMES, DIGITS, vtype=GRB.BINARY, name="is")
    pin = {x: model.addVar(lb=0, ub=9, vtype=GRB.INTEGER, name=x) for x in NAMES}
    for x in NAMES:
        model.addConstr(is_.sum(x, "*") == 1, name=f"one_digit[{x}]")
        model.addConstr(pin[x] == gp.quicksum(v * is_[x, v] for v in DIGITS), name=f"read[{x}]")

    # No two digits are the same.
    for v in DIGITS:
        model.addConstr(is_.sum("*", v) <= 1, name=f"different[{v}]")

    a, b, c, d = (pin[x] for x in NAMES)

    # The two-digit number cd is 3 times the two-digit number ab.
    model.addConstr(10 * c + d == 3 * (10 * a + b), name="cd_is_3_ab")

    # The two-digit number da is 2 times the two-digit number bc.
    model.addConstr(10 * d + a == 2 * (10 * b + c), name="da_is_2_bc")

    return model, {x: pin[x] for x in NAMES}
