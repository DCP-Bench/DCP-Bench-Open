Company manufactures shirts, shorts, pants; each product p makes x_p units, 0 <= x_p <= max_production.
  -> unary integer per product: xs[p][i] = (x_p >= i+1), chain If(xs[p][i+1], xs[p][i]), x_p = sum(xs[p]).
Each product requires labor hours and cloth (use[p][r] per unit, capacity[r] per resource).
  -> per resource r: sum over p and i of use[p][r] * xs[p][i] <= capacity[r] (weights <= 6).
All products can only be manufactured by renting their machine (product[p][1] is the machine of product p).
  -> y[m] Bool per machine; If(xs[p][0], y[m]) for m = machine of p (x_p >= 1 needs the machine rented).
Renting cost of each rented machine is paid (renting_cost[m] * y[m]).
Profit of products excluding renting: product[p][0] per unit.
Objective: maximise z = sum(product[p][0] * x_p) - sum(renting_cost[m] * y[m]).
  -> output z is that same expression; ("maximize", z).
