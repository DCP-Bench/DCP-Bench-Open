The grocery problem's product is taken in dollars: the product of the cent prices equals total * 100^(n-1), so the sum-only reading (sum = product = total) is unsat on the 711 example. Read the instance notes to pin down unit conventions before modelling.
A chain of `mult` over the prices with domain 1..total*100^(n-1) keeps every intermediate bounded, since all prices are at least 1.
