Problem: six men each charge a price; the pair totals are given; find each charge. Satisfaction.
Paper hanger and painter together are paid $1,100 -> linear(x_ph + x_pa == 1100, IPL_DOM)
Painter and plumber together are paid $1,700 -> linear(x_pa + x_pl == 1700, IPL_DOM)
Plumber and electrician together are paid $1,100 -> linear(x_pl + x_el == 1100, IPL_DOM)
Electrician and carpenter together are paid $3,300 -> linear(x_el + x_ca == 3300, IPL_DOM)
Carpenter and mason together are paid $5,300 -> linear(x_ca + x_ma == 5300, IPL_DOM)
Mason and painter together are paid $3,200 -> linear(x_ma + x_pa == 3200, IPL_DOM)
  (six two-variable equations, one per pair; no global row fits a weighted pair sum, linear is the row for it)
Each charge is non-negative and at most 5300 (the largest pair total) -> domain 0..5300 on the array
Branching: all six charges, INT_VAR_SIZE_MIN, INT_VAL_MIN (the system has a unique solution; branching is a formality)
Objective: none (satisfaction)
