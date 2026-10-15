Four lathes with skilled operators each work 40 hours, so 160 lathe-hours per week -> linear(*this, IntArgs({3, 2}), x, IRT_LQ, 160) (3 h per small set, 2 h per large set; cap 160)
Only 200 kg of boxwood per week can be obtained -> linear(*this, IntArgs({1, 3}), x, IRT_LQ, 200) (1 kg per small set, 3 kg per large set; cap 200)
Decide how many small sets and large sets to make each week -> IntVar small_set, large_set in 0..max, each bounded by the lathe row (160/3, 160/2)
Large set profit $20, small set profit $5, maximise profit -> max_profit = expr(*this, linear(IntArgs({5, 20}), x)); maximize(max_profit)
Branching: no other decisions; branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MAX()) on the two decisions, then the profit is fixed by propagation
Outputs small_set, large_set, max_profit -> output(...) with the IntVars
