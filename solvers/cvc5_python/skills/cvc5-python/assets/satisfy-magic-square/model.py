"""Satisfy: a 3x3 magic square using each of 1..9 once.

Shows: integer variables with bounds, Distinct, linear sums, status check.
"""
from cvc5.pythonic import *

N = 3
TARGET = N * (N * N + 1) // 2  # 15 for N = 3

cells = [[Int(f"c_{i}_{j}") for j in range(N)] for i in range(N)]
flat = [c for row in cells for c in row]

s = SolverFor("QF_LIA")
s.add(*[And(c >= 1, c <= N * N) for c in flat])
s.add(Distinct(flat))
for row in cells:
    s.add(Sum(row) == TARGET)
for j in range(N):
    s.add(Sum([cells[i][j] for i in range(N)]) == TARGET)
s.add(Sum([cells[i][i] for i in range(N)]) == TARGET)
s.add(Sum([cells[i][N - 1 - i] for i in range(N)]) == TARGET)

result = s.check()
if result == sat:
    m = s.model()
    for row in cells:
        print(" ".join(str(m.eval(c, model_completion=True).as_long()) for c in row))
    print(f"line sum {TARGET}")
elif result == unsat:
    print("no magic square")
else:
    print(f"undecided: {s.reason_unknown()}")
