"""All 3 x 3 Latin squares: every row and column holds 1..3 once. There are 12."""
from pycsp3 import *

n = 3
grid = VarArray(size=[n, n], dom=range(1, n + 1))

satisfy(
    # every row has distinct values
    [AllDifferent(grid[i]) for i in range(n)],
    # every column has distinct values
    [AllDifferent(grid[:, j]) for j in range(n)],
)

status = solve(sols=ALL)
# n_solutions() misreads counts of 1000 or more ("1,500" -> 500): count the stored values instead
count = len(grid[0][0].values) if status is SAT else 0
# SAT does not say whether the search finished: ACE writes "d COMPLETE EXPLORATION" to its log
with open(solver().last_log) as log:
    complete = "d COMPLETE EXPLORATION" in log.read()

for k in range(count):
    print(values(grid, sol=k))
print("Solutions:", count)
print("Complete:", complete)
