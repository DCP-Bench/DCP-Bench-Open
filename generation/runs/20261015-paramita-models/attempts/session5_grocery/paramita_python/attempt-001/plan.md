# Plan: session5_grocery

Requirements (description words) -> Paramita encoding

- "a kid buys a number of items" -> num_items prices, one per item: `p[i][d]` one-hot over the candidate prices
- "the cashier charges a total price" -> the prices add up to total_price: `sum(d * p[i][d]) == total_price`
- "I multiplied the items instead of adding them ... with adding them the price still comes to the same total price" -> the product of the prices, read in dollars (the instance notes check out only this way: 2 items [200,200] give 2*2 = 400), equals total_price: the product of the cent prices is total_price * 100^(n-1). Prefix-product reachability over the divisors M of that product: `r[j][e]` = product of the first j prices is e, `If(r[j-1][e0] & p[j-1][d], r[j][e0*d])`, final `r[n][M]`.
- "What were the prices of the items? ... in cents, as a list of integers" -> output `prices[i] = sum(d * p[i][d])`, length num_items
- Candidate prices: positive divisors of M that are at most total_price (each divides M; each is at most the sum). Bounds derived from the statement.

Objective: none (satisfaction).
