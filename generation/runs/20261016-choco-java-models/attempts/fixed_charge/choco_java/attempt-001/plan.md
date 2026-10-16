A company manufactures shirts, shorts, and pants. -> 3 products, make[p] in 0..max_production
Each product requires a number of hours of labor and a certain amount of cloth -> labor and cloth use per unit: use[p][r]
the company has a limited capacity of both -> sum_p use[p][r] * make[p] <= capacity[r] (scalar, per resource)
all of these products can be manufactured only by renting an appropriate machine -> make[p] <= max_production * rent[machine(p)] (scalar with big-M)
machines rented for a fixed cost -> rent[k] BoolVar, renting_cost[k]
The profit on the products (excluding the cost of renting the equipment) -> profit[p] = product[p][0]
maximize its profit -> objective z = sum profit[p]*make[p] - sum renting_cost[k]*rent[k], MAXIMIZE z
