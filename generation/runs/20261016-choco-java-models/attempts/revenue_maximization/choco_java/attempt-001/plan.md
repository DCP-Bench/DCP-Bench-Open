Flight legs with a limited passenger capacity -> available_seats[l] per leg
Packages: each package uses some legs (delta[p][l] = 1) -> membership from delta
Demand: sell at most the estimated demand of each package -> x[p] in 0..demand[p]
We reserve the passenger seats according to the number of packages sold -> for each leg: sum over packages of delta[p][l] * x[p] <= available_seats[l]
Revenue of a package is its price; maximize the total revenue -> max_revenue = sum revenue[p] * x[p]; objective MAXIMIZE max_revenue
Print the units of each package to sell (packages_to_sell) -> output x
