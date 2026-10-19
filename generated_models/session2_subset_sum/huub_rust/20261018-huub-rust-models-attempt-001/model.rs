// Session 2 subset sum: a bank van carried several bags of coins. Each bag type holds a
// given number of coins (coin_numbers). Thieves stole some bags, and a given total number
// of coins (total_coins_lost) was lost. Find how many bags were stolen for each bag type.
// The output bags lists one count per bag type.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let total = inst.int("total_coins_lost");
    let coins = inst.ints("coin_numbers");

    // For each bag type, the number of stolen bags is a non-negative integer. No more bags
    // of a type can be stolen than fit into the total number of coins lost.
    let bags: Vec<View<i64>> = coins
        .iter()
        .map(|&c| m.new_int_decision(0..=total / c))
        .collect();

    // The coins of all stolen bags add up to the total number of coins lost.
    let lost = bags
        .iter()
        .zip(coins.iter())
        .map(|(&x, &c)| x * c)
        .sum::<IntLinearExp>();
    eq2(m, lost, total)?;

    let mut out = Out::new();
    out.put("bags", bags);
    Ok(out)
}
