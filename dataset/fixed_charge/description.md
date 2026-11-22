A company manufactures shirts, shorts, and pants. Each
product requires a number of hours of labor and a certain amount of
cloth, and the company has a limited capacity of both. In addition,
all of these products can be manufactured only by renting an appropriate
machine, each product having its own machine type. The renting cost of a
machine is paid once, however much is made on it. The profit on the products
(excluding the cost of renting the equipment) is also known, per unit, and
each product is made in a whole number of units. The company would like to
maximize its profit: the profit on the units made, less the cost of the
machines rented.

The data gives:

- `renting_cost[m]`: the one-off cost of renting machine type `m`.
- `capacity[r]`: the available amount of resource `r`, where resource `labor` (index 0) is labor hours and `cloth` (index 1) is cloth.
- `product[p] = [profit, machine]`: for product `p`, the profit per unit made and the index of the machine type it needs.
- `use[p][r]`: the amount of resource `r` needed to make one unit of product `p`.
- `max_production`: an upper bound on the number of units of any single product.
- `shirt`, `shorts`, `pants` (product indices), `shirtM`, `shortM`, `pantM` (machine indices), `labor`, `cloth` (resource indices), and the index lists `products`, `machines`, `resources` with their lengths `num_products`, `num_machines`, only name positions in the arrays above; all indices are 0-based.

Print the maximum profit that the company can make (z).
