from pycsp3 import *

# choose how many units of each package to sell so that the seats of each flight leg are not exceeded
# and the revenue is maximal
n_packages = len(data.demand)
n_legs = len(data.available_seats)

# packages_to_sell[p] is the number of units of package p sold, at most its estimated demand
packages_to_sell = VarArray(size=n_packages, dom=range(0, max(data.demand) + 1))

# max_revenue is the total revenue of the units sold
max_revenue = Var(dom=range(0, sum(data.revenue) * max(data.demand) + 1))

satisfy(
    # no more units of a package are sold than its estimated demand
    [packages_to_sell[p] <= data.demand[p] for p in range(n_packages)],
    # the passenger seats reserved on each leg must not exceed the seats available on that leg
    [Sum(data.delta[p][l] * packages_to_sell[p] for p in range(n_packages)) <= data.available_seats[l]
     for l in range(n_legs)],
    # the revenue is the price of each unit times the number of units sold
    max_revenue == Sum(data.revenue[p] * packages_to_sell[p] for p in range(n_packages)),
)

# maximise the total revenue
maximize(max_revenue)
