// Archery puzzle: how close can the young archer come to scoring a total of a
// target score using as many arrows as she pleases? The targets are given as a
// list of integers. Print the number of hits on each target (hits).

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let t = inst.ints("targets");
    let target = inst.int("target_score");
    let max_ring = *t.iter().max().unwrap();

    // Any optimal solution has a total of at most target + max_ring: a larger
    // total could drop one arrow and get closer to the target. So each hit
    // count is bounded by that total divided by its ring value.
    let cap = target + max_ring;
    let hits: Vec<View<i64>> = t.iter().map(|&v| m.new_int_decision(0..=cap / v)).collect();

    // The total score is the sum of the ring values times the hits.
    let total = m.new_int_decision(0..=cap);
    m.linear(
        hits[0] * t[0]
            + hits[1] * t[1]
            + hits[2] * t[2]
            + hits[3] * t[3]
            + hits[4] * t[4]
            + hits[5] * t[5],
    )
    .eq(total)
    .post()?;

    // The deviation is the absolute difference between the total and the target.
    // It is minimised, so the two inequalities pin it to |total - target|.
    let dev = m.new_int_decision(0..=target);
    m.linear(total - dev).le(target).post()?;
    m.linear(total + dev).ge(target).post()?;

    let mut out = Out::new();
    out.put("hits", hits);
    out.minimise(dev);
    Ok(out)
}
