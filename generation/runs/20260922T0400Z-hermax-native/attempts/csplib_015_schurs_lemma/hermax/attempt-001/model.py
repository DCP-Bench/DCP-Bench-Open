# Put balls 1..n into c boxes so no triple x + y = z shares a box.
from hermax.model import Model


def build(instance):
    n = instance["n"]
    boxes = instance["c"]

    m = Model()
    balls = m.int_vector("balls", n, 1, boxes)
    for x in range(1, n):
        for y in range(1, n - x + 1):
            z = x + y
            if z <= n:
                # No box holds all three at once.
                for box in range(1, boxes + 1):
                    m &= (~(balls[x - 1] == box) | ~(balls[y - 1] == box)
                          | ~(balls[z - 1] == box))
    return m, {"balls": balls}
