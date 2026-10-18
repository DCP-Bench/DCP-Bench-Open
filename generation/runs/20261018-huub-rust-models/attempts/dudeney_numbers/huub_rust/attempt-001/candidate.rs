// Dudeney numbers: a positive integer that is a perfect cube such that the sum
// of its digits is equal to the cube root of the number. Print such a number
// (number) that is also larger than 1. The number has at most n digits.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");

    // The number is below 10^n, so its cube root is at most the largest c with c^3 < 10^n.
    let mut limit: i64 = 1;
    for _ in 0..n {
        limit *= 10;
    }
    let mut cmax: i64 = 1;
    while (cmax + 1) * (cmax + 1) * (cmax + 1) < limit {
        cmax += 1;
    }

    // A perfect cube larger than 1: the cube root c is at least 2, and number = c * c * c.
    let c = m.new_int_decision(2..=cmax);
    let sq = m.new_int_decision(4..=cmax * cmax);
    m.mul(c, c).result(sq).post()?;
    let number = m.new_int_decision(8..=limit - 1);
    m.mul(sq, c).result(number).post()?;

    // The number has at most n digits: digits d_0..d_{n-1}, each from 0 to 9.
    let ds = m.new_int_decisions(n, 0..=9);
    let mut pow10: Vec<i64> = Vec::with_capacity(n);
    let mut p: i64 = 1;
    for _ in 0..n {
        pow10.push(p);
        p *= 10;
    }

    // The digits written in base ten give the number.
    m.linear(
        ds.iter()
            .zip(pow10.iter())
            .map(|(d, w)| *d * *w)
            .sum::<IntLinearExp>(),
    )
    .eq(number)
    .post()?;

    // The sum of its digits is equal to the cube root of the number.
    m.linear(ds.iter().copied().sum::<IntLinearExp>())
        .eq(c)
        .post()?;

    let mut out = Out::new();
    out.put("number", number);
    Ok(out)
}
