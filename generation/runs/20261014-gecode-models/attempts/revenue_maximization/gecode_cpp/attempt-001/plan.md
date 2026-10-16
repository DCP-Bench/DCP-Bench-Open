Problem: sell packages of flight itineraries to maximise revenue, subject to seat capacity on each leg.

- units of each package sold (packages_to_sell) -> IntVarArray x of length np = len(demand), x[p] in 0..demand[p]
- each package is sold at most its estimated demand -> domain upper bound demand[p] on x[p]
- seats reserved on a leg are the units of every package that uses it -> for each leg l: linear(*this, ones, {x[p] : delta[p][l] = 1}, IRT_LQ, available_seats[l]) (linear, bounds propagation; coefficients all 1)
- total revenue is the sum of revenue[p] * x[p] -> total = expr(*this, sum(revenue[p] * x[p])) as an IntVar (max_revenue)
- branching: branch on the package units (decisions) with INT_VAR_SIZE_MIN and INT_VAL_MAX (sell as many units as seats allow first)
- objective: maximize total revenue -> maximize(total)
