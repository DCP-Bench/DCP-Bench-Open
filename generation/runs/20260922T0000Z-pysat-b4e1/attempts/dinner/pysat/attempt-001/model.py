# Twenty people at dinner for twenty dollars.
# The prices and party sizes are the puzzle, so the instance carries no fields.
from dcp_sat import Sat


def build(instance):
    sat = Sat()
    grandparents = sat.int(1, 6)
    parents = sat.int(1, 10)
    children = sat.int(1, 40)

    # $3, $2 and $0.50 a head, doubled to clear the half dollar.
    sat.linear_eq([(6, grandparents), (4, parents), (1, children)], 40)
    sat.linear_eq([(1, grandparents), (1, parents), (1, children)], 20)
    return sat, {"grandparents": grandparents, "parents": parents,
                 "children": children}
