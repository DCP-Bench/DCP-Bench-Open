// Money change: Alice has to give Bob change of a given amount. There are
// different types of coins with different values, and a limited number of
// coins of each type is available. Compose the change from the available
// coins while minimizing the number of coins used. Output coin_counts: the
// number of coins of each type to give to Bob.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let amount = inst.int("amount");
    let values = inst.ints("types_of_coins");
    let available = inst.ints("available_coins");
    let n = values.len();

    // She has a certain number of coins of each value available: the change
    // is composed with the available coins, one count per type of coin.
    // A type cannot give more coins than are available, nor more coins than
    // fit in the amount.
    let mut counts = Vec::with_capacity(n);
    for i in 0..n {
        let max_fit = amount / values[i];
        let upper = available[i].min(max_fit);
        counts.push(m.new_int_decision(0..=upper));
    }

    // Alice has to give Bob some change of the given amount: the coins given
    // must add up to the amount exactly. Sum of count_i * value_i == amount.
    let total_value = counts
        .iter()
        .zip(values.iter())
        .map(|(c, v)| *c * *v)
        .sum::<IntLinearExp>();
    m.linear(total_value).eq(amount).post()?;

    // Minimizing the number of coins used: the objective is the total count.
    let max_total: i64 = (0..n).map(|i| available[i].min(amount / values[i])).sum();
    let coin_total = m.new_int_decision(0..=max_total);
    let total_coins = counts.iter().copied().sum::<IntLinearExp>();
    m.linear(total_coins).eq(coin_total).post()?;

    let mut out = Out::new();
    out.put("coin_counts", counts);
    out.minimise(coin_total);
    Ok(out)
}
