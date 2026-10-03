"""Crypta: a 20-digit cryptarithmetic addition in which the letters A..J are distinct digits and no number starts with 0."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    # The puzzle has no instance data: the letters and the addition, split into three
    # blocks of digits with carries Sr1 and Sr2 as in the reference, are the puzzle's own.
    names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    digits = range(10)

    model = gp.Model("crypta")
    # Coefficients reach 10^7; tighten the integrality tolerance so the rounded digits
    # satisfy the equations exactly.
    model.Params.IntFeasTol = 1e-9

    # is_[L, v] is 1 when letter L stands for digit v; each letter is one digit and the
    # letters are distinct digits.
    is_ = model.addVars(names, digits, vtype=GRB.BINARY, name="is")
    for L in names:
        model.addConstr(is_.sum(L, "*") == 1, name=f"one_digit[{L}]")
    for v in digits:
        model.addConstr(is_.sum("*", v) <= 1, name=f"distinct[{v}]")
    value = {L: gp.quicksum(v * is_[L, v] for v in digits) for L in names}
    A, B, C, D, E, F, G, H, I, J = (value[L] for L in names)

    # The first letter of each number (B, D, G) is not zero.
    for L in ("B", "D", "G"):
        model.addConstr(is_[L, 0] == 0, name=f"leading[{L}]")

    # Carries between the three blocks of the addition.
    sr1 = model.addVar(vtype=GRB.BINARY, name="Sr1")
    sr2 = model.addVar(vtype=GRB.BINARY, name="Sr2")

    # Lowest seven digits of the sum, carrying Sr1 out.
    model.addConstr(A + 10 * E + 100 * J + 1000 * B + 10000 * B + 100000 * E + 1000000 * F
                    + E + 10 * J + 100 * E + 1000 * F + 10000 * G + 100000 * A + 1000000 * F
                    == F + 10 * E + 100 * E + 1000 * H + 10000 * I + 100000 * F + 1000000 * B
                    + 10000000 * sr1, name="block1")

    # Middle seven digits, taking Sr1 in and carrying Sr2 out.
    model.addConstr(C + 10 * F + 100 * H + 1000 * A + 10000 * I + 100000 * I + 1000000 * J
                    + F + 10 * I + 100 * B + 1000 * D + 10000 * I + 100000 * D + 1000000 * C + sr1
                    == J + 10 * F + 100 * A + 1000 * F + 10000 * H + 100000 * D + 1000000 * D
                    + 10000000 * sr2, name="block2")

    # Highest six digits, taking Sr2 in.
    model.addConstr(A + 10 * J + 100 * J + 1000 * I + 10000 * A + 100000 * B
                    + B + 10 * A + 100 * G + 1000 * F + 10000 * H + 100000 * D + sr2
                    == C + 10 * A + 100 * G + 1000 * E + 10000 * J + 100000 * G, name="block3")

    return model, value
