from pycsp3 import *

# Fixed charge: a company makes shirts, shorts and pants. Each product needs labour and
# cloth, and a machine that must be rented, at a fixed cost, before any of that product is made.
# We maximise profit: product sales minus the rent of the machines used.
num_products = data.num_products
num_machines = data.num_machines
max_production = data.max_production
profit = [data.product[p][0] for p in range(num_products)]
machine_of = [data.product[p][1] for p in range(num_products)]
use = data.use
capacity = data.capacity
renting_cost = data.renting_cost

# production[p] is the number of units of product p made
production = VarArray(size=num_products, dom=range(0, max_production + 1))

# rented[m] is 1 when machine m is rented
rented = VarArray(size=num_machines, dom={0, 1})

# z is the profit from sales minus the rent
z = Var(dom=range(-sum(renting_cost), sum(profit) * max_production + 1))

satisfy(
    # a product can only be made on a machine that is rented
    [production[p] <= max_production * rented[machine_of[p]] for p in range(num_products)],
    # the labour and cloth used by all products stay within the capacity of each resource
    [Sum(use[p][r] * production[p] for p in range(num_products)) <= capacity[r]
     for r in range(len(capacity))],
    # the profit is the sales of all products minus the rent of all machines
    z == Sum(profit[p] * production[p] for p in range(num_products))
         - Sum(renting_cost[m] * rented[m] for m in range(num_machines)),
)

# maximise the profit
maximize(z)
