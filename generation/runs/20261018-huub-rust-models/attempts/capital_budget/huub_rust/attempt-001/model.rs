// Capital budgeting: a company considers a number of investments. Each investment has a net
// present value (npv) and a certain cash outflow (cash_flow) at the present time. There is a
// total budget available for investment. Choose the investments that maximise the total NPV.
// Output x: whether each investment is chosen (booleans). Output z: the total NPV (integer).

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let npv = inst.ints("npv");
    let cash_flow = inst.ints("cash_flow");
    let budget = inst.int("budget");
    let n = npv.len();

    // Each investment is chosen (1) or not (0), as an integer 0/1 variable.
    let pick: Vec<View<i64>> = (0..n).map(|_| m.new_int_decision(0..=1)).collect();

    // The total outflow of the chosen investments must not exceed the available budget.
    let cost: IntLinearExp = (0..n).map(|i| pick[i] * cash_flow[i]).sum();
    m.linear(cost).le(budget).post()?;

    // The total NPV of the chosen investments is the objective.
    let max_npv: i64 = npv.iter().sum();
    let total = m.new_int_decision(0..=max_npv);
    let value: IntLinearExp = (0..n).map(|i| pick[i] * npv[i]).sum();
    m.linear(value).eq(total).post()?;

    // The Boolean output x[i] is true exactly when investment i is chosen.
    let mut chosen: Vec<View<bool>> = Vec::with_capacity(n);
    for i in 0..n {
        chosen.push(m.linear(pick[i]).eq(1).reify());
    }

    let mut out = Out::new();
    out.put("x", chosen).put("z", total);
    out.maximise(total);
    Ok(out)
}
