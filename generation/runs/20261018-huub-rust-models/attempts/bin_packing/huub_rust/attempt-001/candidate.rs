// Bin packing: assign each item to one of num_bins bins of a fixed capacity, so
// that the total weight of the items in each bin does not exceed the capacity.
// Output bins[i] is the 0-based bin of item i.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let weights = inst.ints("weights");
    let capacity = inst.int("capacity");
    let num_bins = inst.int("num_bins");

    // Each item is assigned to one bin, numbered 0..num_bins.
    let bins: Vec<View<i64>> = (0..weights.len())
        .map(|_| m.new_int_decision(0..=num_bins - 1))
        .collect();

    // The total weight of the items in each bin does not exceed the capacity.
    for b in 0..num_bins {
        let load: IntLinearExp = bins
            .iter()
            .zip(weights.iter())
            .map(|(x, &w)| x.eq(b) * w)
            .sum();
        m.linear(load).le(capacity).post()?;
    }

    let mut out = Out::new();
    out.put("bins", bins);
    Ok(out)
}
