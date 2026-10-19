// Bin packing: given several items of specific weights and a number of bins of a
// fixed capacity, assign each item to a bin so that the total weight of the items in
// each bin does not exceed the capacity. Output bins: the bin of each item, 0-indexed.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let weights = inst.ints("weights");
    let capacity = inst.int("capacity");
    let num_bins = inst.size("num_bins");
    let n = weights.len();

    // Each item is assigned to one bin, numbered 0..num_bins.
    let bins: Vec<IntVar> = (0..n).map(|_| IntVar::new(0..=(num_bins as i64) - 1)).collect();

    // The total weight of the items in each bin does not exceed the capacity.
    // lit[i][b] is true when item i is in bin b.
    let mut lit: Vec<Vec<Lit>> = Vec::with_capacity(n);
    for i in 0..n {
        let mut row = Vec::with_capacity(num_bins);
        for b in 0..num_bins {
            let bv = bins[i].equals(s, b as i64)?;
            row.push(lit_of(s, bv)?);
        }
        lit.push(row);
    }
    for b in 0..num_bins {
        let mut e = LinExp::default();
        for i in 0..n {
            e += LinExp::from(lit[i][b]) * weights[i];
        }
        post(s, e, Comparator::LessEq, capacity)?;
    }

    let mut out = Out::new();
    out.put("bins", &bins);
    Ok(out)
}
