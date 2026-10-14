from pycsp3 import *

# choose how many coins of each denomination to have, so that every amount below the maximum can be paid exactly
# with the minimum total number of coins
n = len(data.denominations)
M = data.max_amount_to_pay
d = data.denominations

# x[i] is the number of coins of denomination i
x = VarArray(size=n, dom=range(0, M))

# c[a][i] is the number of coins of denomination i used to pay the amount a + 1
c = VarArray(size=[M - 1, n], dom=range(0, M))

satisfy(
    # the coins used to pay an amount must be coins that were bought
    [c[a][i] <= x[i] for a in range(M - 1) for i in range(n)],
    # every amount smaller than the maximum must be paid exactly
    [Sum(d[i] * c[a][i] for i in range(n)) == a + 1 for a in range(M - 1)],
)

# minimise the total number of coins
minimize(Sum(x))
