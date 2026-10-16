A company is considering a number of investments -> one Boolean x[i] per investment (x[i] = 1 if chosen), x = BoolVarArray(*this, n, 0, 1)
Each investment will yield a net present value (NPV) -> npv[i] from the instance, weights for the objective
Each investment requires a certain cash outflow at the present time -> cash_flow[i] from the instance
There is a total budget available for investment -> budget from the instance
the total cash outflow of the chosen investments must not exceed the budget -> linear(*this, IntArgs(cash_flow), x, IRT_LQ, budget, IPL_DEF)
Maximize the NPV obtained from the investments -> z = IntVar in [0, sum npv]; z == sum npv[i]*x[i] -> linear(*this, IntArgs(npv), x, IRT_EQ, z, IPL_DOM); maximize(z)
Print whether each investment is chosen (x) as a list of booleans -> output("x", x)
Print the total NPV (z) as an integer -> output("z", z)
Branching -> branch(*this, x, BOOL_VAR_NONE(), BOOL_VAL_MAX()): decide each investment, taking it first (value 1 first suits maximisation)
