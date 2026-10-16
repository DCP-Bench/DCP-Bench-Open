"""n-queens: one queen per row, columns counted from 1. Usage: python model.py [n]"""
import sys

from pycsp3 import *

n = int(sys.argv[1]) if len(sys.argv) > 1 else 8

# q[i] is the column of the queen in row i, counted from 1
q = VarArray(size=n, dom=range(1, n + 1))

satisfy(
    # no two queens share a column
    AllDifferent(q),
    # no two queens share a diagonal
    AllDifferent(q[i] + i for i in range(n)),
    AllDifferent(q[i] - i for i in range(n)),
)

status = solve()
if status is SAT:
    print("Status: SAT")
    print("Columns:", values(q))
elif status is UNSAT:
    print("Status: UNSAT")
else:
    print("Status: UNKNOWN (limit hit or solver error; see the solver_*.log file)")
