"""SEND + MORE = MONEY: give each letter a different digit so that the sum holds."""
import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data: the words of the puzzle are mirrored here.
LETTERS = "sendmory"
DIGITS = range(10)


def build(instance):
    model = gp.Model("send_more_money")

    # is_[L, d] = 1 when letter L stands for digit d; digit[L] reads it back.
    is_ = model.addVars(LETTERS, DIGITS, vtype=GRB.BINARY, name="is")
    digit = {L: model.addVar(lb=0, ub=9, vtype=GRB.INTEGER, name=L) for L in LETTERS}
    for L in LETTERS:
        model.addConstr(is_.sum(L, "*") == 1, name=f"one_digit[{L}]")
        model.addConstr(digit[L] == gp.quicksum(d * is_[L, d] for d in DIGITS), name=f"read[{L}]")

    # Each letter is a different digit.
    for d in DIGITS:
        model.addConstr(is_.sum("*", d) <= 1, name=f"different[{d}]")

    def word(w):
        return gp.quicksum(10 ** (len(w) - 1 - k) * digit[ch] for k, ch in enumerate(w))

    # SEND + MORE = MONEY.
    model.addConstr(word("send") + word("more") == word("money"), name="sum")

    # The first letter of each word is not zero.
    model.addConstr(digit["s"] >= 1, name="s_leading")
    model.addConstr(digit["m"] >= 1, name="m_leading")

    return model, {L: digit[L] for L in "sendmory"}
