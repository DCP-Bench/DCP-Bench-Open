// Twelve-pack problem: given a target number of items and a set of pack sizes,
// choose how many packs of each size to use so that the total number of items
// meets or exceeds the target, as close to the target as possible (minimise the
// total). Output: counts[i] is the number of packs of size packs[i].

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    // The target and the pack sizes come from the instance; there is one count per pack size.
    let target = inst.int("target");
    let packs = inst.ints("packs");
    let pmax = packs.iter().copied().max().unwrap_or(1);

    // Every optimal total is at most target + pmax - 1: filling with the largest
    // pack up to the target gives a total below that bound. Each count is therefore
    // bounded by that total divided by its pack size.
    let top = (target + pmax - 1).max(target);

    // The number of packs of each size.
    let counts: Vec<View<i64>> = packs
        .iter()
        .map(|&p| m.new_int_decision(0..=(top / p).max(0)))
        .collect();

    // The total number of items bought, which is minimised.
    let total = m.new_int_decision(target..=top);

    // The total items bought, sum over sizes of count * size, equals the total.
    let items = counts
        .iter()
        .zip(packs.iter())
        .map(|(c, &p)| *c * p)
        .sum::<IntLinearExp>();
    m.linear(items).eq(total).post()?;

    let mut out = Out::new();
    out.put("counts", counts);
    out.minimise(total);
    Ok(out)
}
