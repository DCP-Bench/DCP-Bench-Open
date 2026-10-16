# PyCSP3 star-imports its vocabulary, as every PyCSP3 model does.
# ruff: noqa: F403, F405
from pycsp3 import *

n = data.n
x = Var(range(n + 1))
y = Var(range(n + 1))
if data.optimize:
    satisfy(x + y >= n)
    minimize(x + y)
else:
    satisfy(x + y == n)
