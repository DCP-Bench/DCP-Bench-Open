// Cutting stock problem: raw rolls of width roll_width are cut into pieces of the
// given widths. Each cutting pattern p yields num_rolls_width[p][w] pieces of width
// widths[w]. Decide how many times each pattern is cut so that the total number of
// rolls cut is minimal, with every width cut at least its order count.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let pats = inst.matrix("num_rolls_width");
    let orders = inst.ints("orders");
    let np = pats.len();
    let nw = orders.len();
    let total: i64 = orders.iter().sum();

    // Number of times each pattern is cut, bounded by the total demand.
    let used: Vec<View<i64>> = (0..np).map(|_| m.new_int_decision(0..=total)).collect();

    // The number of pieces of each width cut must meet its order.
    // The pieces cut of width w are the sum over patterns of rolls[p][w] * used[p].
    for w in 0..nw {
        let pieces: IntLinearExp = (0..np).map(|p| used[p] * pats[p][w]).sum();
        m.linear(pieces).ge(orders[w]).post()?;
    }

    // Objective: the total number of rolls cut.
    let rolls: IntLinearExp = used.iter().copied().sum();
    let min_rolls = m.new_int_decision(0..=total * np as i64);
    m.linear(rolls).eq(min_rolls).post()?;

    let mut out = Out::new();
    out.put("patterns_used", used).put("min_rolls_cut", min_rolls);
    out.minimise(min_rolls);
    Ok(out)
}
