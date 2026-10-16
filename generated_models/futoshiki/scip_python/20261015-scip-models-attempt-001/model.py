# Futoshiki: fill an n x n grid with the digits 1..n so that every row and every column
# holds each digit once, the given digits stay, and each inequality sign between two
# neighbouring squares holds.
from pyscipopt import Model, quicksum


def build(instance):
    values = instance["values"]
    lt = instance["lt"]
    n = len(values)
    m = Model()

    # b[i, j, v]: the square in row i, column j (0-based) holds the digit v
    b = {(i, j, v): m.addVar(name=f"b_{i}_{j}_{v}", vtype="B")
         for i in range(n) for j in range(n) for v in range(1, n + 1)}
    # the square holds exactly one digit
    for i in range(n):
        for j in range(n):
            m.addCons(quicksum(b[i, j, v] for v in range(1, n + 1)) == 1)

    # the digit of each square, as an integer
    grid = {}
    for i in range(n):
        for j in range(n):
            grid[i, j] = m.addVar(name=f"grid_{i}_{j}", vtype="I", lb=1, ub=n)
            m.addCons(grid[i, j] == quicksum(v * b[i, j, v] for v in range(1, n + 1)))

    # each row contains each digit once
    for i in range(n):
        for v in range(1, n + 1):
            m.addCons(quicksum(b[i, j, v] for j in range(n)) == 1)
    # each column contains each digit once
    for j in range(n):
        for v in range(1, n + 1):
            m.addCons(quicksum(b[i, j, v] for i in range(n)) == 1)

    # the digits given at the start of the puzzle (0 marks an empty square)
    for i in range(n):
        for j in range(n):
            if values[i][j] > 0:
                m.addCons(b[i, j, values[i][j]] == 1)

    # each inequality sign: the first square is smaller than its neighbour
    # the instance gives 1-based row and column numbers
    for r1, c1, r2, c2 in lt:
        m.addCons(grid[r1 - 1, c1 - 1] + 1 <= grid[r2 - 1, c2 - 1])

    out = [[grid[i, j] for j in range(n)] for i in range(n)]
    return m, {"grid": out}
