from pycsp3 import *

# prices of the players in each group, in GBP millions as the statement gives them
goalkeepers = [0.73, 1.28, 3.88]
defenders = [0.92, 1.31, 1.62, 2.41, 2.79, 3.28, 3.91, 4.57]
midfielders = [1.8, 2.63, 3.17, 3.769, 4.14, 4.75, 5.38, 5.93, 6.78, 7.13]
strikers = [4.46, 6.47, 7.78, 8.39, 9.5]

# the prices in GBP thousands, so that all coefficients are integers
def thousands(prices):
    return [round(p * 1000) for p in prices]

BUDGET = 30000  # the chairman's limit of GBP 30 million, in thousands

gk = VarArray(size=len(goalkeepers), dom={0, 1})
df = VarArray(size=len(defenders), dom={0, 1})
md = VarArray(size=len(midfielders), dom={0, 1})
st = VarArray(size=len(strikers), dom={0, 1})

# z is the total price of the selected players, in GBP thousands
z = Var(dom=range(0, BUDGET + 1))

satisfy(
    # the total price is the sum of the prices of the players bought
    z == Sum(thousands(goalkeepers)[i] * gk[i] for i in range(len(gk)))
    + Sum(thousands(defenders)[i] * df[i] for i in range(len(df)))
    + Sum(thousands(midfielders)[i] * md[i] for i in range(len(md)))
    + Sum(thousands(strikers)[i] * st[i] for i in range(len(st))),
    # the total must not go over the limit of GBP 30 million
    z <= BUDGET,
    # you must buy exactly one goalkeeper
    Sum(gk) == 1,
    # you must buy 2 or more defenders
    Sum(df) >= 2,
    # you must buy 3 or more midfielders
    Sum(md) >= 3,
    # you must buy 2 or more strikers
    Sum(st) >= 2,
    # you must buy at least eleven players in total
    Sum(gk) + Sum(df) + Sum(md) + Sum(st) >= 11,
)

# you want to spend as much money as you can
maximize(z)
