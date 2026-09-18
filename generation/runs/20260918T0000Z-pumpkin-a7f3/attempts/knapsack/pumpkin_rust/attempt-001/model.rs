// Maximise the value carried without exceeding the knapsack capacity.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let values = inst.ints("values");
    let weights = inst.ints("weights");
    let capacity = inst.int("capacity");

    let x = cp.bools(values.len());
    cp.bool_le(&weights, &x, capacity);

    let total: i32 = values.iter().sum();
    let profit = cp.int(0, total);
    cp.bool_sum_eq(&values, &x, profit);

    let mut m = Model::new();
    m.put("x", x);
    m.maximise(profit);
    m
}
