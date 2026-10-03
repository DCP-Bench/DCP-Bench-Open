"""Hanging weights: give the weights A-M distinct values 1..13 so that every bar of the mobile balances."""
import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data: thirteen weights, values 1..13, and the
# balance equations of the drawn mobile.
NAMES = "abcdefghijklm"
VALUES = range(1, 14)


def build(instance):
    model = gp.Model("hanging_weights")

    # is_[w, v] = 1 when weight w has value v; each weight has one value and,
    # the weights being all different, each value is used once.
    is_ = model.addVars(NAMES, VALUES, vtype=GRB.BINARY, name="is")
    w = {}
    for name in NAMES:
        model.addConstr(is_.sum(name, "*") == 1, name=f"one_value[{name}]")
        w[name] = model.addVar(lb=1, ub=13, vtype=GRB.INTEGER, name=name)
        model.addConstr(w[name] == gp.quicksum(v * is_[name, v] for v in VALUES), name=f"read[{name}]")
    for v in VALUES:
        model.addConstr(is_.sum("*", v) <= 1, name=f"different[{v}]")
    a, b, c, d, e, f, g, h, i, j, k, l, m = (w[n] for n in NAMES)

    # Each bar balances: weight times distance from the pivot is equal on
    # both sides, and a bar below counts as its total weight.
    model.addConstr(4 * a == b, name="bar_ab")                       # A and B
    model.addConstr(5 * c == d, name="bar_cd")                       # C and D
    model.addConstr(3 * e == 2 * f, name="bar_ef")                   # E and F
    model.addConstr(3 * g == 2 * (c + d), name="bar_g_cd")           # G and the C-D bar
    model.addConstr(3 * (a + b) + 2 * j == k + 2 * (g + c + d), name="bar_j_k")   # J, K and the bars below
    model.addConstr(3 * h == 2 * (e + f) + 3 * i, name="bar_h_i")    # H, I and the E-F bar
    model.addConstr(h + i + e + f == l + 4 * m, name="bar_l_m")      # L, M and the H-I bar
    model.addConstr(4 * (l + m + h + i + e + f) == 3 * (j + k + g + a + b + c + d), name="top_bar")

    return model, {n: w[n] for n in NAMES}
