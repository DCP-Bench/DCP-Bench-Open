from pycsp3 import *

# one yes/no choice per investment
n = len(data.npv)
x = VarArray(size=n, dom={0, 1})
# total NPV of the chosen investments
z = Var(dom=range(0, sum(data.npv) + 1))

satisfy(
    # the sum of all chosen investments must be less than the budget
    Sum(data.cash_flow[i] * x[i] for i in range(n)) <= data.budget,
    # the total NPV is the sum of the NPVs of the chosen investments
    z == Sum(data.npv[i] * x[i] for i in range(n)),
)

# maximise the total NPV
maximize(z)
