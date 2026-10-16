Given the prices and the nutritional requirements (at least) for each nutrition type, what is the optimal diet -> food counts x[i] (i over 4 foods) in 0..ub, one IntVar per food
Type of food table: calories 400/200/150/500, chocolate 3/2/0/0, sugar 2/2/4/4, fat 2/4/1/5 (fixed by the problem) -> per nutrient: scalar(x, row, ">=", limit) with limits from the instance
The optimal diet is to minimize the cost of the products -> cost = scalar(x, price, "=", cost) with prices from the instance; setObjective MINIMIZE cost
Print the optimal cost of the diet (cost) -> out.put("cost", cost)
