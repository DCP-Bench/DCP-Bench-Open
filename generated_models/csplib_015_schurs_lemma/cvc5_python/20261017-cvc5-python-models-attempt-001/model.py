# csplib 015, Schur's lemma: put the balls 1..n into c boxes so that for any
# triple of balls (x, y, z) with x + y = z, not all three are in the same box.
# Output "balls": balls[i] is the box (1..c) of ball i + 1.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    c = instance["c"]
    balls = [cz.Int(f"ball_{i}") for i in range(n)]
    constraints = []

    # Each ball is in exactly one box, numbered 1 to c.
    for b in balls:
        constraints.append(b >= 1)
        constraints.append(b <= c)

    # For any triple of balls with x + y = z (x and y may be equal), and each box j,
    # not all of x, y and z are in box j.
    for x in range(1, n + 1):
        for y in range(x, n + 1):
            z = x + y
            if z > n:
                break
            for j in range(1, c + 1):
                constraints.append(
                    cz.Or(balls[x - 1] != j, balls[y - 1] != j, balls[z - 1] != j)
                )

    return constraints, {"balls": balls}
