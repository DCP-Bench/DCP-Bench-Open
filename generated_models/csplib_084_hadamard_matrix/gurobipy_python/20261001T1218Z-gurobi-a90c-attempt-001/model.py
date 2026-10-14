"""Hadamard matrix Legendre pairs: two +-1 sequences a, b of odd length l, each summing to 1, with PAF(A, s) + PAF(B, s) = -2 for s = 1..(l-1)/2."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    l = instance["l"]  # sequence length, odd
    m = (l - 1) // 2  # number of autocorrelation constraints
    idx = range(l)

    model = gp.Model("hadamard_matrix")

    # Each entry is -1 or +1. up[i] is 1 when the entry is +1, so the entry is
    # 2 * up[i] - 1; this keeps the model linear (a product of two variables
    # would drop the licence limit to 200 variables).
    up_a = [model.addVar(vtype=GRB.BINARY, name=f"up_a[{i}]") for i in idx]
    up_b = [model.addVar(vtype=GRB.BINARY, name=f"up_b[{i}]") for i in idx]
    a = [2 * u - 1 for u in up_a]
    b = [2 * u - 1 for u in up_b]

    # Each sequence sums to 1.
    model.addConstr(gp.quicksum(a) == 1, name="sum_a")
    model.addConstr(gp.quicksum(b) == 1, name="sum_b")

    # The product of two +-1 entries is 1 when they agree and -1 when they
    # differ, so PAF(A, s) = l - 2 * (number of i where a[i] != a[i+s mod l]).
    # differ[i] is that disagreement, the XOR of the two up bits, stated with
    # its four linear inequalities.
    def disagreements(up, s, tag):
        total = []
        for i in idx:
            j = (i + s) % l
            d = model.addVar(vtype=GRB.BINARY, name=f"differ_{tag}[{s},{i}]")
            model.addConstr(d >= up[i] - up[j])
            model.addConstr(d >= up[j] - up[i])
            model.addConstr(d <= up[i] + up[j])
            model.addConstr(d <= 2 - up[i] - up[j])
            total.append(d)
        return gp.quicksum(total)

    # PAF(A, s) + PAF(B, s) = -2 for s = 1..m (indices taken mod l).
    for s in range(1, m + 1):
        paf_a = l - 2 * disagreements(up_a, s, "a")
        paf_b = l - 2 * disagreements(up_b, s, "b")
        model.addConstr(paf_a + paf_b == -2, name=f"paf[{s}]")

    return model, {"a": a, "b": b}
