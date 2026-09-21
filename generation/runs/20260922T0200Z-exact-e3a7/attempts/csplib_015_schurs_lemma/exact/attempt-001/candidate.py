# Put balls 1..n into c boxes so no triple x + y = z shares a box.
from dcp_pb import Pb


def build(instance):
    n = instance["n"]
    boxes = instance["c"]

    pb = Pb()
    balls = pb.ints(n, 1, boxes)
    for x in range(1, n):
        for y in range(1, n - x + 1):
            z = x + y
            if z <= n:
                # No box holds all three at once.
                for box in range(1, boxes + 1):
                    pb.at_most([pb.is_value(balls[x - 1], box),
                                pb.is_value(balls[y - 1], box),
                                pb.is_value(balls[z - 1], box)], 2)
    return pb, {"balls": balls}
