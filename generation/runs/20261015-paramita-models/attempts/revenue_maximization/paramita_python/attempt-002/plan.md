We have a set of flight legs (one-way non-stop flight) with a limited passenger capacity -> per leg l: sum_j delta[j][l] * x_j <= available_seats[l], PB over unary sums.
We defined a set of flight itineraries to sell as a package with a given price -> package j has price revenue[j].
For each package, we have an estimated demand -> x_j in 0..demand[j]: unary Bools x_j_ge_k for k = 1..demand[j], If(x_j_ge_{k+1}, x_j_ge_k), value x_j = sum of the bits.
How many units of each package should we sell -> packages_to_sell[j] = x_j (integer expression).
We reserve the passenger seats according to the number of packages we want to sell -> the seat constraint above uses the same unit counts x_j.
Maximize the revenue -> objective: sum_j revenue[j] * x_j, output max_revenue is the same expression.
