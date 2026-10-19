// Bananas: buy 100 fruits for exactly 100 dollars. All four fruit types must be
// bought (at least one each). Minimise the number of bananas and apples.
//
// Prices, in dollars: 5 bananas cost 3, 7 oranges cost 5, 9 mangoes cost 7,
// 3 apples cost 9. Scaled by 315 (the least common multiple of 5, 7, 9, 3) so
// every coefficient is an integer: a banana costs 189, an orange 225, a mango
// 245, an apple 945, and the total is 100 * 315 = 31500.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // all types of fruits need to be purchased
    let bananas = m.new_int_decision(1..=100);
    let oranges = m.new_int_decision(1..=100);
    let mangoes = m.new_int_decision(1..=100);
    let apples = m.new_int_decision(1..=100);

    // purchase 100 fruits
    m.linear(bananas + oranges + mangoes + apples).eq(100).post()?;

    // in 100 dollars (scaled by 315)
    m.linear(bananas * 189 + oranges * 225 + mangoes * 245 + apples * 945)
        .eq(31500)
        .post()?;

    // bananas and apples should be of minimum quantity
    let objective = m.new_int_decision(0..=200);
    m.linear(bananas + apples).eq(objective).post()?;

    let mut out = Out::new();
    out.put("apples", apples)
        .put("bananas", bananas)
        .put("mangoes", mangoes)
        .put("oranges", oranges);
    out.minimise(objective);
    Ok(out)
}
