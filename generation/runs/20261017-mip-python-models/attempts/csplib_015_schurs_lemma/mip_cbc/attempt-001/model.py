# CSPLib 015: Schur's lemma. Put n balls labelled 1..n into c boxes so that for
# any triple of balls (x, y, z) with x + y = z, not all three are in the same box.
# Output "balls": for each ball i (1..n), its box number from 1 to c.
import mip


def build(instance):
    n = instance["n"]
    c = instance["c"]
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # M[i][j] = 1 if ball i+1 is in box j+1
    M = [[model.add_var(f"M_{i}_{j}", var_type=mip.BINARY) for j in range(c)]
         for i in range(n)]

    # a ball must be in exactly one box
    for i in range(n):
        model += mip.xsum(M[i][j] for j in range(c)) == 1

    # for each x + y = z, and each box, not (x, y and z all in that box)
    for x in range(1, n + 1):
        for y in range(1, n + 1):
            z = x + y
            if z > n:
                continue
            # x = y repeats a ball, so the sum is built with xsum (a + a loses a coefficient)
            for j in range(c):
                model += mip.xsum([M[x - 1][j], M[y - 1][j], M[z - 1][j]]) <= 2

    # the box of each ball as an integer from 1 to c
    balls = []
    for i in range(n):
        b = model.add_var(f"ball_{i}", lb=1, ub=c, var_type=mip.INTEGER)
        model += b == mip.xsum((j + 1) * M[i][j] for j in range(c))
        balls.append(b)

    return model, {"balls": balls}
