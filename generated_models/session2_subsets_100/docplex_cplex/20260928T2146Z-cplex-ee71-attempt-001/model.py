"""Equal subsets: find two disjoint non-empty subsets S and T of A with the same sum."""
from docplex.mp.model import Model


def build(instance):
    A = instance["A"]
    n = len(A)

    model = Model("subsets_100")

    # in_S[i] and in_T[i] are 1 when element i is in S or in T.
    in_S = model.binary_var_list(n, name="in_S")
    in_T = model.binary_var_list(n, name="in_T")

    # The elements of S add up to the same sum as those of T.
    model.add_constraint(model.dot(in_S, A) == model.dot(in_T, A), ctname="equal_sums")

    # S and T are disjoint: no element is in both.
    for i in range(n):
        model.add_constraint(in_S[i] + in_T[i] <= 1, ctname=f"disjoint_{i}")

    # S and T are non-empty.
    model.add_constraint(model.sum(in_S) >= 1, ctname="S_nonempty")
    model.add_constraint(model.sum(in_T) >= 1, ctname="T_nonempty")

    return model, {"in_S": in_S, "in_T": in_T}
