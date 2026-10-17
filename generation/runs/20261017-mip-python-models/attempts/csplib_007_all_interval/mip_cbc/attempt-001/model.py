# csplib_007 all-interval series of size n: find a permutation x of 0..n-1 such that
# the interval vector diffs[i] = |x[i+1] - x[i]| (i = 0..n-2) is a permutation of 1..n-1.
# n is read from the instance.
import mip


def build(instance):
    n = instance["n"]
    model = mip.Model(solver_name="CBC")

    # one-hot binaries: p[i][v] = 1 when position i holds pitch-class v
    p = [[model.add_var(f"p_{i}_{v}", var_type=mip.BINARY) for v in range(n)]
         for i in range(n)]
    x = [model.add_var(f"x_{i}", lb=0, ub=n - 1, var_type=mip.INTEGER)
         for i in range(n)]

    # the series s is a permutation of Z_n: each pitch class occurs exactly once
    for i in range(n):
        model += mip.xsum(p[i]) == 1
        model += x[i] == mip.xsum(v * p[i][v] for v in range(n))
    for v in range(n):
        model += mip.xsum(p[i][v] for i in range(n)) == 1

    # the interval vector d[i] = |x[i+1] - x[i]| is a permutation of 1..n-1
    # absolute value: s[i] = 1 selects the sign x[i+1] - x[i] >= 0; the big-M is
    # 2(n-1), the largest gap between d and a difference of two values in 0..n-1
    m_big = 2 * (n - 1)
    d = [model.add_var(f"d_{i}", lb=1, ub=n - 1, var_type=mip.INTEGER)
         for i in range(n - 1)]
    s = [model.add_var(f"s_{i}", var_type=mip.BINARY) for i in range(n - 1)]
    for i in range(n - 1):
        model += d[i] >= x[i + 1] - x[i]
        model += d[i] >= x[i] - x[i + 1]
        model += d[i] <= (x[i + 1] - x[i]) + m_big * (1 - s[i])
        model += d[i] <= (x[i] - x[i + 1]) + m_big * s[i]

    # the interval vector is a permutation of 1..n-1: one-hot per interval value
    q = [[model.add_var(f"q_{i}_{k}", var_type=mip.BINARY) for k in range(1, n)]
         for i in range(n - 1)]
    for i in range(n - 1):
        model += mip.xsum(q[i]) == 1
        model += d[i] == mip.xsum(k * q[i][k - 1] for k in range(1, n))
    for k in range(1, n):
        model += mip.xsum(q[i][k - 1] for i in range(n - 1)) == 1

    return model, {"x": x, "diffs": d}
