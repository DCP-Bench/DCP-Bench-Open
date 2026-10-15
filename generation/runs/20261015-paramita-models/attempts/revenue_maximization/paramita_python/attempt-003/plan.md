We have a set of flight legs (one-way non-stop flight) with a limited passenger capacity -> per leg l: sum_j delta[j][l] * units_j <= available_seats[l], PB over binary sums.
We defined a set of flight itineraries to sell as a package with a given price -> package j has price revenue[j].
For each package, we have an estimated demand -> units_j in 0..demand[j]: binary bits b_j_k with weight 2^k, units_j = sum_k 2^k b_j_k, and units_j <= demand[j].
How many units of each package should we sell -> packages_to_sell[j] = units_j (integer expression).
We reserve the passenger seats according to the number of packages we want to sell -> the seat constraint above uses the same unit counts units_j.
Maximize the revenue -> objective: sum_j revenue[j] * units_j, output max_revenue is the same expression.
