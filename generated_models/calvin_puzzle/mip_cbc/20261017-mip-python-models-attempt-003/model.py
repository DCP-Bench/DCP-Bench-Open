# Calvin puzzle: fill an n by n grid so that every square holds one of the numbers 1..n^2,
# each used once, and the sequence of numbers follows the movement rules below.
# Output x is the completed grid as a list of lists of integers.
import mip


def build(instance):
    n = instance["n"]
    N = n * n
    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    cells = [(i, j) for i in range(n) for j in range(n)]

    # p[v][i][j] = 1 when the number v+1 sits in the square (i, j)
    p = [
        [[m.add_var(f"p_{v}_{i}_{j}", var_type=mip.BINARY) for j in range(n)] for i in range(n)]
        for v in range(N)
    ]
    x = [[m.add_var(f"x_{i}_{j}", lb=1, ub=N, var_type=mip.INTEGER) for j in range(n)] for i in range(n)]

    # Every square holds exactly one number, and the grid entry is that number
    for i, j in cells:
        m += mip.xsum(p[v][i][j] for v in range(N)) == 1
        m += x[i][j] == mip.xsum((v + 1) * p[v][i][j] for v in range(N))

    # Each number 1..n^2 is placed in exactly one square
    for v in range(N):
        m += mip.xsum(p[v][i][j] for i, j in cells) == 1

    # Movement Type I: the next number is placed exactly three squares away vertically or
    # horizontally (a two square gap). Movement Type II: the next number is placed exactly
    # two squares away diagonally (a one square gap).
    steps = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]

    # q[k][i][j][o] = 1 when the number k+1 sits in (i, j) and the number k+2 is reached
    # from it by step o. Each square of k+1 chooses exactly one step, and that step lands
    # on the square of k+2.
    for k in range(N - 1):
        landing = [[[] for _ in range(n)] for _ in range(n)]
        for i, j in cells:
            qs = []
            for o, (a, b) in enumerate(steps):
                ti, tj = i + a, j + b
                if 0 <= ti < n and 0 <= tj < n:
                    q = m.add_var(f"q_{k}_{i}_{j}_{o}", var_type=mip.BINARY)
                    m += q <= p[k][i][j]
                    m += q <= p[k + 1][ti][tj]
                    qs.append(q)
                    landing[ti][tj].append(q)
            # the next number is placed by exactly one of the allowed steps from this square
            m += mip.xsum(qs) == p[k][i][j]
        # the square of the next number is reached by exactly one step from the square
        # of the number before it
        for ti, tj in cells:
            m += mip.xsum(landing[ti][tj]) == p[k + 1][ti][tj]

    return m, {"x": x}
