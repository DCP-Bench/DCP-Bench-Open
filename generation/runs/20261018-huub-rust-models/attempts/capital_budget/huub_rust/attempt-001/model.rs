// Capital budgeting: a company considers a number of investments. Each investment has a net
// present value (npv) and a certain cash outflow (cash_flow) at the present time. There is a
// total budget available for investment. Choose the investments that maximise the total NPV.
// Output x: whether each investment is chosen (booleans). Output z: the total NPV (integer).

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let npv = inst.ints("npv");
    let cash_flow = inst.ints("cash_flow");
    let budget = inst.int("budget");
    let n = npv.len();

    // Decision: is investment i chosen.
    let x: Vec<View<bool>> = (0..n).map(|_| m.new_bool_decision()).collect();

    // The total outflow of the chosen investments must not exceed the available budget.
    let mut cost = IntLinearExp::from(0i64);
    for i in 0..n {
        cost = cost + IntLinearExp::from(x[i]) * cash_flow[i];
    }
    m.linear(cost).le(budget).post()?;

    // The total NPV of the chosen investments is the objective.
    let max_npv: i64 = npv.iter().sum();
    let total = m.new_int_decision(0..=max_npv);
    let mut value = IntLinearExp::from(0i64);
    for i in 0..n {
        value = value + IntLinearExp::from(x[i]) * npv[i];
    }
    m.linear(value).eq(total).post()?;

    let mut out = Out::new();
    out.put("x", x).put("z", total);
    out.maximise(total);
    Ok(out)
}
