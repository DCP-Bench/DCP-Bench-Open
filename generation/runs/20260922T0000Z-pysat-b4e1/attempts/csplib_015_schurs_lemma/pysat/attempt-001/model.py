# Put balls 1..n into c boxes so no triple x + y = z shares a box.
from dcp_sat import Sat


def build(instance):
    n = instance["n"]
    boxes = instance["c"]

    sat = Sat()
    balls = sat.ints(n, 1, boxes)
    for x in range(1, n):
        for y in range(1, n - x + 1):
            z = x + y
            if z <= n:
                # No box holds all three at once.
                for box in range(1, boxes + 1):
                    sat.clause([-balls[x - 1].literal(box),
                                -balls[y - 1].literal(box),
                                -balls[z - 1].literal(box)])
    return sat, {"balls": balls}
