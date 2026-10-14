"""General store: an alphametic in which sixteen words add up to ALL WOOL, each letter a different digit."""
import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data: the words of the sign are mirrored here.
ADDENDS = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
           "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"]
TOTAL = "ALLWOOL"
LETTERS = "CHESABOWPL"
DIGITS = range(10)


def build(instance):
    model = gp.Model("general_store")

    # is_[L, d] = 1 when letter L stands for digit d; digit[L] reads it back.
    is_ = model.addVars(LETTERS, DIGITS, vtype=GRB.BINARY, name="is")
    digit = {L: model.addVar(lb=0, ub=9, vtype=GRB.INTEGER, name=L) for L in LETTERS}
    for L in LETTERS:
        model.addConstr(is_.sum(L, "*") == 1, name=f"one_digit[{L}]")
        model.addConstr(digit[L] == gp.quicksum(d * is_[L, d] for d in DIGITS), name=f"read[{L}]")

    # Each different letter stands for a different digit.
    for d in DIGITS:
        model.addConstr(is_.sum("*", d) <= 1, name=f"different[{d}]")

    # The words add up to ALL WOOL. Written with place values the equation has
    # coefficients up to 10^6, where a 1e-5 integrality tolerance on one digit
    # moves the sum by 10; the same addition is posted column by column with
    # carries instead, as done by hand, which keeps every coefficient small.
    width = max(len(TOTAL), max(len(w) for w in ADDENDS))
    max_carry = (len(ADDENDS) * 9 + len(ADDENDS)) // 10
    carry = [model.addVar(lb=0, ub=max_carry, vtype=GRB.INTEGER, name=f"carry[{c}]") for c in range(width + 1)]
    model.addConstr(carry[0] == 0, name="no_carry_into_units")
    model.addConstr(carry[width] == 0, name="no_carry_out")
    for c in range(width):
        column = gp.quicksum(digit[w[-1 - c]] for w in ADDENDS if c < len(w))
        result = digit[TOTAL[-1 - c]] if c < len(TOTAL) else 0
        model.addConstr(column + carry[c] == result + 10 * carry[c + 1], name=f"column[{c}]")

    return model, {L: digit[L] for L in LETTERS}
