// Choose investments to maximise net present value within the budget.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let npv = inst.ints("npv");
    let cash_flow = inst.ints("cash_flow");
    let budget = inst.int("budget");

    let x = cp.bools(npv.len());
    cp.bool_le(&cash_flow, &x, budget);

    let z = cp.int(0, npv.iter().sum());
    cp.bool_sum_eq(&npv, &x, z);

    let mut m = Model::new();
    m.put("x", x);
    m.put("z", z);
    m.maximise(z);
    m
}
