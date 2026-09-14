import z3


def build(instance):
    n = instance["n"]
    boxes = instance["c"]
    balls = [z3.Int(f"balls_{i}") for i in range(n)]
    constraints = [z3.And(box >= 1, box <= boxes) for box in balls]
    # No triple x + y = z may sit entirely in one box.
    for x in range(1, n):
        for y in range(1, n - x + 1):
            z = x + y
            if z <= n:
                constraints.append(z3.Or(balls[x - 1] != balls[y - 1],
                                         balls[x - 1] != balls[z - 1],
                                         balls[y - 1] != balls[z - 1]))
    return constraints, {"balls": balls}
