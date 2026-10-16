# Problem: Choose production quantities within their bounds, under the time limit, to maximize the total profit.
from math import lcm
from pycsp3 import *

a = data.a
b = data.b
c = data.c
u = data.u
n = len(a)
# clear the fractions 1 / a[j] by multiplying the time limit by L
L = lcm(*a)
# x[j] is the production quantity of product j
x = VarArray(size=n, dom=lambda j: range(u[j] + 1))
total_profit = Var(dom=range(0, sum(c[j] * u[j] for j in range(n)) + 1))
satisfy(
    # the total time used, sum of x[j] / a[j], is at most b
    Sum(L // a[j] * x[j] for j in range(n)) <= b * L,
    # the total profit is the sum of c[j] * x[j]
    total_profit == Sum(c[j] * x[j] for j in range(n)),
)
# maximize the total profit
maximize(total_profit)
