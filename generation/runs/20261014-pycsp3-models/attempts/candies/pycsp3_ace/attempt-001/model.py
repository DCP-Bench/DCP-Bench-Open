from pycsp3 import *

# Give candies to children sitting in a line, each child at least one candy,
# so that a child with a higher rating than a neighbour gets more candies,
# and minimise the total number of candies.

ratings = data.ratings
n = len(ratings)

# x[i] is the number of candies given to child i
x = VarArray(size=n, dom=range(1, n + 1))

# z is the total number of candies
z = Var(dom=range(n, n * n + 1))

satisfy(
    # a child with a higher rating than the neighbour gets more candies
    [x[i] > x[i + 1] for i in range(n - 1) if ratings[i] > ratings[i + 1]],
    [x[i] < x[i + 1] for i in range(n - 1) if ratings[i] < ratings[i + 1]],

    # the total number of candies is the sum over all children
    z == Sum(x),
)

# minimise the total number of candies
minimize(z)
