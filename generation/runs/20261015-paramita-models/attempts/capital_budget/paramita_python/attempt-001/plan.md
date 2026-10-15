Requirement: "A company is considering a number of investments." -> x[i] = Bool per investment i, one per entry of npv.
Requirement: "Each investment will yield a net present value (NPV)." -> z = sum(npv[i] * x[i]) (total NPV, integer expression over Bools; no encoding needed, weighted sum).
Requirement: "Each investment requires a certain cash outflow at the present time." -> cash_flow[i] is the outflow of investment i.
Requirement: "There is a total budget available for investment." -> sum(cash_flow[i] * x[i]) <= budget (PB constraint, direct weighted sum).
Objective: "How to maximize the NPV obtained from the investments?" -> maximize z.
Outputs: x = list of 4 Bools (x[i] chosen); z = total NPV integer expression.
