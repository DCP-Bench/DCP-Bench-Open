# 100 bushels among 100 people: 3 per man, 2 per woman, half per child,
# with five times as many women as men.
# The puzzle statement fixes every number, so the instance carries no fields.
from dcp_sat import Sat


def build(instance):
    sat = Sat()
    # Five times as many women as men caps the men at 20 within 100 people,
    # which keeps the one-hot encodings small.
    men = sat.int(0, 20)
    women = sat.int(0, 100)
    children = sat.int(0, 100)

    sat.linear_eq([(1, men), (1, women), (1, children)], 100)
    # Doubled to clear the child's half bushel.
    sat.linear_eq([(6, men), (4, women), (1, children)], 200)
    sat.linear_eq([(5, men), (-1, women)], 0)
    return sat, {"men": men, "women": women, "children": children}
