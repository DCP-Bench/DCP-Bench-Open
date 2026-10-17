# Travelling salesman problem: find a shortest tour that visits every city exactly once
# and returns to the start. Edge cost is the Euclidean distance between the two points,
# rounded to an integer. Output: the optimal travel distance (travel_distance).
# Tour as a binary x[i][j] per directed edge; subtours ruled out by lifted
# Miller-Tucker-Zemlin position constraints (Desrochers-Laporte form).
import math

import mip


def build(instance):
    pts = instance["locations"]
    n = len(pts)
    cost = [[int(math.floor(math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1]) + 0.5))
             for j in range(n)] for i in range(n)]

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    x = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                x[i][j] = model.add_var(f"x_{i}_{j}", var_type=mip.BINARY)

    # Each city is left exactly once
    for i in range(n):
        model.add_constr(mip.xsum(x[i][j] for j in range(n) if j != i) == 1)

    # Each city is entered exactly once
    for j in range(n):
        model.add_constr(mip.xsum(x[i][j] for i in range(n) if i != j) == 1)

    # No city pair is traversed in both directions (a 2-cycle is a subtour)
    for i in range(n):
        for j in range(i + 1, n):
            model.add_constr(x[i][j] + x[j][i] <= 1)

    # The tour is a single cycle through all cities: no subtours.
    # Position variables u[j] in 1..n-1 for the non-origin cities; the origin 0 has position 0.
    # Lifted Miller-Tucker-Zemlin constraints for every ordered pair (i, j) with j not the origin.
    u = [None] * n
    for j in range(1, n):
        u[j] = model.add_var(f"u_{j}", lb=1, ub=n - 1, var_type=mip.INTEGER)
    for i in range(n):
        for j in range(1, n):
            if i == j:
                continue
            if i == 0:
                model.add_constr((n - 1) * x[i][j] + (n - 3) * x[j][i] - u[j] <= n - 2)
            else:
                model.add_constr(u[i] - u[j] + (n - 1) * x[i][j] + (n - 3) * x[j][i] <= n - 2)

    # Travel distance is the sum of the rounded edge distances of the chosen edges
    travel = mip.xsum(cost[i][j] * x[i][j] for i in range(n) for j in range(n) if i != j)
    model.objective = travel

    return model, {"travel_distance": travel}
