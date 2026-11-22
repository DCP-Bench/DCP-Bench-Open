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

`renting_cost` holds the renting cost of each machine type, and `capacity` the available labor hours and cloth.
For each product (shirts, shorts and pants, in that order), `product` gives its profit per unit and the machine type it
needs, counted from 0, and `use` gives the labor hours and cloth needed for one unit. No product is made in more than
`max_production` units.

Print the maximum profit that the company can make (z).
