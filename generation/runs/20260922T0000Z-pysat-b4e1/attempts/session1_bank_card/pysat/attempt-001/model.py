# A four digit PIN abcd with cd = 3*ab and da = 2*bc, all digits distinct.
# The clues are the puzzle, so the instance carries no fields.
from dcp_sat import Sat


def build(instance):
    sat = Sat()
    digits = sat.ints(4, 0, 9)
    a, b, c, d = digits
    sat.all_different(digits)

    # 10c + d == 3 * (10a + b)
    sat.linear_eq([(10, c), (1, d), (-30, a), (-3, b)], 0)
    # 10d + a == 2 * (10b + c)
    sat.linear_eq([(10, d), (1, a), (-20, b), (-2, c)], 0)
    return sat, {"a": a, "b": b, "c": c, "d": d}
