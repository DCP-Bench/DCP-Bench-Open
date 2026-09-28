"""Equal subsets: find two disjoint non-empty subsets S and T of A with the same sum."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    A = instance["A"]
    elements = range(len(A))

    model = gp.Model("subsets_100")

    # in_S[i] and in_T[i] are 1 when element i is in S or in T.
    in_S = model.addVars(elements, vtype=GRB.BINARY, name="in_S")
    in_T = model.addVars(elements, vtype=GRB.BINARY, name="in_T")

    # The elements of S add up to the same sum as those of T.
    model.addConstr(gp.quicksum(A[i] * in_S[i] for i in elements)
                    == gp.quicksum(A[i] * in_T[i] for i in elements), name="equal_sums")

    # S and T are disjoint: no element is in both.
    for i in elements:
        model.addConstr(in_S[i] + in_T[i] <= 1, name=f"disjoint[{i}]")

    # S and T are non-empty.
    model.addConstr(in_S.sum() >= 1, name="S_nonempty")
    model.addConstr(in_T.sum() >= 1, name="T_nonempty")

    return model, {"in_S": [in_S[i] for i in elements], "in_T": [in_T[i] for i in elements]}
