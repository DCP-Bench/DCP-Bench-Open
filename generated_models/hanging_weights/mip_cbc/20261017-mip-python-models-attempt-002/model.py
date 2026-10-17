# Hanging weights puzzle: choose whole weights a..m, each from 1 to 13, so that every bar of
# the hanging diagram balances. Satisfaction problem. The instance has no data fields, so the
# model takes its numbers from the diagram and the description.
#
# The rules in the description: the weights on either side of a pivot must balance when
# weighted by distance from the pivot, and a bar hanging beneath another contributes its
# total weight as if it were a single weight. The description gives 5*C = D and 3*G = 2*(C+D).
# Weights are distinct, which the puzzle requires.
import mip


NAMES = "abcdefghijklm"
VALUES = list(range(1, 14))


def build(instance):
    mdl = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # one-hot encoding: each weight takes exactly one value from 1..13, and no value repeats
    x = {}
    for n in NAMES:
        for val in VALUES:
            x[n, val] = mdl.add_var(f"x_{n}_{val}", var_type=mip.BINARY)
    w = {}
    for n in NAMES:
        w[n] = mdl.add_var(n, lb=1, ub=13, var_type=mip.INTEGER)
        # the weight is exactly one of its values
        mdl.add_constr(mip.xsum(x[n, val] for val in VALUES) == 1, f"one_{n}")
        mdl.add_constr(w[n] == mip.xsum(val * x[n, val] for val in VALUES), f"link_{n}")
    # all weights differ: each value is used at most once
    for val in VALUES:
        mdl.add_constr(mip.xsum(x[n, val] for n in NAMES) <= 1, f"distinct_{val}")

    a, b, c, d, e, f, g = (w[n] for n in "abcdefg")
    h, i, j, k, l, m = (w[n] for n in "hijklm")

    # bar A-B: A at arm 4 on the left, B at arm 1 on the right, so 4*A = B
    mdl.add_constr(mip.xsum([4 * a]) == mip.xsum([b]), "bar_AB")

    # bar C-D: 5*C = D, from the description
    mdl.add_constr(mip.xsum([5 * c]) == mip.xsum([d]), "bar_CD")

    # bar E-F: 3*E = 2*F
    mdl.add_constr(mip.xsum([3 * e]) == mip.xsum([2 * f]), "bar_EF")

    # bar G with the bar CD hanging from it: 3*G = 2*(C+D), from the description
    mdl.add_constr(mip.xsum([3 * g]) == mip.xsum([2 * c, 2 * d]), "bar_G_CD")

    # bar J-K: left holds J at arm 2 and bar AB (total A+B) at arm 3;
    # right holds K at arm 1 and the G/CD system (total G+C+D) at arm 2
    mdl.add_constr(
        mip.xsum([3 * a, 3 * b, 2 * j]) == mip.xsum([k, 2 * g, 2 * c, 2 * d]),
        "bar_JK",
    )

    # bar H-I: H at arm 3 on the left; right holds bar EF (total E+F) at arm 2 and I at arm 3
    mdl.add_constr(
        mip.xsum([3 * h]) == mip.xsum([2 * e, 2 * f, 3 * i]),
        "bar_HI",
    )

    # bar L-M: left holds the H-I system (total H+I+E+F) at arm 1;
    # right holds L at arm 1 and M at arm 4
    mdl.add_constr(
        mip.xsum([h, i, e, f]) == mip.xsum([l, 4 * m]),
        "bar_LM",
    )

    # top bar: left is the L-M system (total L+M+H+I+E+F) at arm 4;
    # right is the J-K system (total J+K+G+A+B+C+D) at arm 3
    mdl.add_constr(
        mip.xsum([4 * l, 4 * m, 4 * h, 4 * i, 4 * e, 4 * f])
        == mip.xsum([3 * j, 3 * k, 3 * g, 3 * a, 3 * b, 3 * c, 3 * d]),
        "top_bar",
    )

    return mdl, {n: w[n] for n in NAMES}
