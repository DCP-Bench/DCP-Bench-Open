# Problem: session2_subsets_100. From a set A of distinct integers, find two
# disjoint non-empty subsets S and T whose elements have equal sums.
# Outputs: in_S and in_T, one 0/1 flag per element of A (1 = the element is in the subset).
import mip


def build(instance):
    A = instance["A"]
    n = len(A)
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # in_S[i] = 1 if element i of A is in the subset S
    in_S = [model.add_var(f"in_S_{i}", var_type=mip.BINARY) for i in range(n)]
    # in_T[i] = 1 if element i of A is in the subset T
    in_T = [model.add_var(f"in_T_{i}", var_type=mip.BINARY) for i in range(n)]

    # S and T are disjoint: an element cannot be in both
    for i in range(n):
        model.add_constr(in_S[i] + in_T[i] <= 1)

    # S is non-empty
    model.add_constr(mip.xsum(in_S) >= 1)

    # T is non-empty
    model.add_constr(mip.xsum(in_T) >= 1)

    # the sum of the elements of S equals the sum of the elements of T
    model.add_constr(
        mip.xsum(A[i] * in_S[i] for i in range(n))
        == mip.xsum(A[i] * in_T[i] for i in range(n))
    )

    # satisfaction problem: no objective is set
    return model, {"in_S": in_S, "in_T": in_T}
