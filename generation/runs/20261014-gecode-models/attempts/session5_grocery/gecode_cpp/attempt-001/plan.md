Kid buys n items; the price of each item in cents is a positive integer.
  -> IntVarArray p(*this, n, 1, total - (n-1)); the upper bound follows from the other n-1 prices being at least 1.
Cashier's total is the sum of the item prices.
  -> rel(*this, sum(p) == total) via linear(*this, p, IRT_EQ, total) (bounds).
Cashier's total is also the product of the item prices (multiplied instead of added, same total).
  The product is taken in dollars: the product of the cent prices is total * 100^(n-1) (check: [200,200] gives 2.00*2.00 = 400 cents, and the sum-only reading is unsat on the example).
  -> chain of mult over the prices, domains 1..total*100^(n-1); last product == total*100^(n-1). Every price is at least 1, so partial products are bounded by the full product.
Items are interchangeable and the output is a list of prices with no order: sorted non-decreasing.
  -> rel(*this, p[i] <= p[i+1]) for consecutive i (IRT_LQ); a canonical order for the output.
Branching: decisions are the prices; branch in index order with smallest value first. The partial products are fixed once the prices are.
  -> branch(*this, p, INT_VAR_NONE(), INT_VAL_MIN()).
Objective: none (satisfaction).
