// Bales of hay: n bales of hay were weighed in all possible combinations of two.
// The weights of these combinations were written down in numerical order, without
// keeping track of which weight matched which pair of bales. Find the weight of each bale.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let weights = inst.ints("weights");
    let mut sorted_weights = weights.clone();
    sorted_weights.sort();
    let lo_w = sorted_weights[0];
    let hi_w = sorted_weights[sorted_weights.len() - 1];

    // all combinations of two bales, as index pairs
    let pairs: Vec<(usize, usize)> = (0..n)
        .flat_map(|i| (i + 1..n).map(move |j| (i, j)))
        .collect();
    let p = pairs.len();

    // the weight of each bale, from the data's own range of pair weights:
    // with three or more bales, 2*b_i = s_ij + s_ik - s_jk lies between 2*lo_w - hi_w and 2*hi_w - lo_w
    // (one unit of slack covers the integer rounding)
    let lo = (2 * lo_w - hi_w) / 2 - 1;
    let hi = (2 * hi_w - lo_w) / 2 + 1;
    let bales: Vec<View<i64>> = (0..n).map(|_| m.new_int_decision(lo..=hi)).collect();

    // the weight of each combination of two bales
    let sums: Vec<View<i64>> = (0..p).map(|_| m.new_int_decision(lo_w..=hi_w)).collect();

    // the weight of a combination of two bales is the sum of the two bale weights
    for (q, &(i, j)) in pairs.iter().enumerate() {
        m.linear(bales[i] + bales[j] - sums[q]).eq(0).post()?;
    }

    // x[k][q] holds when the k-th weight in the list is the combination q of two bales
    let x: Vec<Vec<View<bool>>> = (0..p)
        .map(|_| (0..p).map(|_| m.new_bool_decision()).collect())
        .collect();

    // each weight in the list is the weight of exactly one combination of two bales
    for k in 0..p {
        let row = x[k].iter().copied().sum::<IntLinearExp>();
        m.linear(row).eq(1).post()?;
    }

    // each combination of two bales has exactly one weight in the list
    for q in 0..p {
        let col = (0..p).map(|k| x[k][q]).sum::<IntLinearExp>();
        m.linear(col).eq(1).post()?;
    }

    // a combination's weight is the listed weight it is matched to
    for k in 0..p {
        for q in 0..p {
            m.linear(sums[q]).eq(weights[k]).implied_by(x[k][q]).post()?;
        }
    }

    let mut out = Out::new();
    out.put("bales", bales);
    Ok(out)
}
