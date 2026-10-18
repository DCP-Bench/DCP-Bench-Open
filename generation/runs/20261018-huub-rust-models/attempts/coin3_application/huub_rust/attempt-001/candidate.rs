// coin3_application: find the minimum number of coins that allows one to pay
// exactly any amount smaller than the maximum amount, using the given denominations.
// Output x[i] is the number of coins of denomination i.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let d = inst.ints("denominations");
    let max = inst.int("max_amount_to_pay");

    // The number of coins of each denomination. Amounts below max never need more
    // than (max - 1) / d[i] coins of one denomination.
    let mut xs = Vec::new();
    let mut total_ub = 0i64;
    for &c in &d {
        let ub = (max - 1) / c;
        total_ub += ub;
        xs.push(m.new_int_decision(0..=ub));
    }

    // Any amount smaller than the maximum amount can be paid exactly with the coins
    // held: for each amount a from 1 to max - 1, pick how many coins of each
    // denomination are used, so that they add up to a.
    for a in 1..max {
        let mut ys = Vec::new();
        for &c in &d {
            ys.push(m.new_int_decision(0..=a / c));
        }

        // The coins used for the amount sum to exactly a.
        let pay = ys.iter().zip(&d).map(|(&y, &c)| y * c).sum::<IntLinearExp>();
        m.linear(pay).eq(a).post()?;

        // The coins used cannot exceed the coins held.
        for (i, &y) in ys.iter().enumerate() {
            m.linear(y - xs[i]).le(0).post()?;
        }
    }

    // The objective is the total number of coins held.
    let total = m.new_int_decision(0..=total_ub);
    let held = xs.iter().map(|&x| x).sum::<IntLinearExp>();
    m.linear(held).eq(total).post()?;

    let mut out = Out::new();
    out.put("x", xs.clone());
    out.minimise(total);
    Ok(out)
}
