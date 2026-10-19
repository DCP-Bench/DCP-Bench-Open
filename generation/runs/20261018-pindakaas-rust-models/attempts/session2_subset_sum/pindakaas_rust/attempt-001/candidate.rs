// Problem: session2_subset_sum. A bank van had several bags of coins, each
// containing a number of coins from a given list (multiple bags of the same
// kind). Some bags were stolen; a total number of coins was lost. Find how
// many bags were stolen for each type of coin bag.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let total = inst.int("total_coins_lost");
    let coins = inst.ints("coin_numbers");

    // Each type of bag is stolen some number of times, from 0 up to the most
    // bags of that type that can fit in the total.
    let mut bags: Vec<IntVar> = Vec::new();
    for &c in &coins {
        bags.push(IntVar::new(0..=total / c));
    }

    // The coins in the stolen bags add up to the total number of coins lost.
    let mut lost = LinExp::default();
    for (x, &c) in bags.iter().zip(coins.iter()) {
        lost += scaled(x, c);
    }
    post(s, lost, Comparator::Equal, total)?;

    let mut out = Out::new();
    out.put("bags", &bags);
    Ok(out)
}
