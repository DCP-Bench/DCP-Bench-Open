# Plan: capital budget (capital_budget)

- choose a subset of the investments -> one BoolVar per investment, x[i] = 1 if investment i is chosen
- the sum of the chosen investments' cash outflows must be within the budget -> m.scalar(x, cash_flow, "<=", budget)
- the total NPV is the sum of the NPVs of the chosen investments -> z = m.scalar(x, npv, "=", z), z in 0..sum(npv)
- objective: maximize the total NPV -> m.setObjective(MAXIMIZE, z)
- outputs: x (booleans), z (total NPV)
