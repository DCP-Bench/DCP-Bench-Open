# Plan: revenue_maximization, attempt 001

- Sell a whole number of units of each package, at most its demand -> unary count per package (u[p][i] = more than i units), If(u[p][i+1], u[p][i]), bits limited to demand[p]
- Each unit of a package reserves one seat on every leg it uses; seats reserved on a leg must not exceed the available seats -> sum of the unary bits of the packages using that leg <= available_seats[leg] (PB, unit coefficients)
- Maximise total revenue: sum of revenue[p] per unit sold -> objective is sum(revenue[p] * bit) over all unary bits (PB, small weights)
- Output packages_to_sell -> integer expression sum(u[p]) per package
- Output max_revenue -> the objective expression
