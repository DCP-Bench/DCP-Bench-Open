# Plan: contracting_costs

Unknowns: charges of paper_hanger (ph), painter (pp), plumber (pl), electrician (el), carpenter (ca), mason (ma). Each is a nonnegative integer.

- $1,100 to the paper hanger and the painter -> ph + pp == 1100 (binary integers, PB equality)
- $1,700 to the painter and plumber -> pp + pl == 1700
- $1,100 to the plumber and electrician -> pl + el == 1100
- $3,300 to the electrician and carpenter -> el + ca == 3300
- $5,300 to the carpenter and mason -> ca + ma == 5300
- $3,200 to the mason and painter -> ma + pp == 3200
- Charges are nonnegative, each at most 5300 (largest payment) -> 13 bits, bit k weight 2^k
- Objective: none (satisfaction; the system has a unique solution)
