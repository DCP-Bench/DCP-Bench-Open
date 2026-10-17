# Autoreferential sequence (autoref).
# Given an integer n > 0 and an integer m >= 0, find a non-empty finite series
# S = (s0, s1, ..., sn, sn+1) such that the conditions below hold. Output s.
import mip


def build(instance):
    n = instance["n"]
    mval = instance["m"]
    length = n + 2  # S has positions 0..n+1
    vmax = max(n, mval)  # largest value any position may take

    model = mip.Model(solver_name="CBC")  # no objective: satisfaction problem

    # s[j] is the value at position j. Positions 0..n take values 0..n;
    # position n+1 is fixed to m below.
    s = [model.add_var(f"s_{j}", lb=0, ub=(n if j <= n else mval), var_type=mip.INTEGER)
         for j in range(length)]
    # x[j][v] = 1 exactly when s[j] == v.
    x = [[model.add_var(f"x_{j}_{v}", var_type=mip.BINARY)
          for v in range(vmax + 1)]
         for j in range(length)]

    # Each position takes exactly one value, and s[j] is that value.
    for j in range(length):
        model += mip.xsum(x[j][v] for v in range(vmax + 1)) == 1
        model += s[j] == mip.xsum(v * x[j][v] for v in range(vmax + 1))

    # there are si occurrences of i in S for each integer i ranging from 0 to n
    for i in range(n + 1):
        model += s[i] == mip.xsum(x[j][i] for j in range(length))

    # sn+1 = m
    model += s[n + 1] == mval

    return model, {"s": s}
