// Assign each item to a bin without exceeding the bin capacity.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let weights = inst.ints("weights");
    let capacity = inst.int("capacity");
    let num_bins = inst.int("num_bins");
    let n = weights.len();

    let bins = cp.ints(n, 0, num_bins - 1);
    for b in 0..num_bins {
        // weight actually placed in bin b, through an indicator per item
        let here: Vec<Lit> = (0..n).map(|j| cp.is(bins[j], b)).collect();
        cp.bool_le(&weights, &here, capacity);
    }

    let mut m = Model::new();
    m.put("bins", bins);
    m
}
