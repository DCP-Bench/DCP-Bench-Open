// Knapsack (0-1): a hiker chooses which items to put in a backpack. Each item has a value
// and a weight. Maximise the total value of the chosen items without exceeding the weight
// capacity of the backpack. Output x lists, per item, whether it is taken.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let values = inst.ints("values");
    let weights = inst.ints("weights");
    let capacity = inst.int("capacity");
    let n = values.len();

    // x[i] is true if item i is taken (one Boolean per item of this instance).
    let x: Vec<View<bool>> = (0..n).map(|_| m.new_bool_decision()).collect();

    // The total weight of the taken items is at most the capacity of the backpack.
    let total_weight = x
        .iter()
        .zip(&weights)
        .map(|(b, &w)| {
            let taken: View<i64> = (*b).into();
            IntLinearExp::from(taken * w)
        })
        .sum::<IntLinearExp>();
    m.linear(total_weight).le(capacity).post()?;

    // The objective is the total value of the taken items.
    let total_value = x
        .iter()
        .zip(&values)
        .map(|(b, &v)| {
            let taken: View<i64> = (*b).into();
            IntLinearExp::from(taken * v)
        })
        .sum::<IntLinearExp>();
    let max_value: i64 = values.iter().sum();
    let profit = m.new_int_decision(0..=max_value);
    m.linear(total_value).eq(profit).post()?;

    let mut out = Out::new();
    out.put("x", x);
    out.maximise(profit);
    Ok(out)
}
