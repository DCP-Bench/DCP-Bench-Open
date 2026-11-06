This is a multi-commodity transportation problem. Given a set of origins `Origins`, a set of destinations `Destinations`,
and a set of products `Products`. Each origin `i` has a certain supply of each product `p` `Supply_{i,p}` and each
destination `j` has a certain demand for each product `p` `Demand_{j,p}`. The cost of shipping one unit of product `p`
from origin `i` to destination `j` is `ShippingCost_{i, j, p}`. The problem aims to minimize the total cost of shipping
all products from the origins to the destinations.

Print the optimized cost (total_cost) as an integer.
