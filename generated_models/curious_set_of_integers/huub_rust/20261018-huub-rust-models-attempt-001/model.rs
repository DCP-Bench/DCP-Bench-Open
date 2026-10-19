// Curious set of integers: the integers 1, 3, 8 and 120 form a set in which the product of
// any two integers is one less than a perfect square. Find a fifth number (>= 0) that can be
// added to the set without destroying this property. Output: number.
// The search range for the number comes from the instance field max_val.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let max_val = inst.int("max_val");

    // The fifth number, between 0 and max_val.
    let x = m.new_int_decision(0..=max_val);

    // The product of the fifth number and each member of the set is one less than a square.
    // Upper bound on the square root of the largest product (120 * max_val + 1), from the data.
    let root_hi = ((120 * max_val + 1) as f64).sqrt() as i64 + 1;
    let set = [1i64, 3, 8, 120];

    // The product of x and a set member, plus one, is a perfect square s * s.
    for a in set {
        let s = m.new_int_decision(0..=root_hi);
        let sq = m.mul(s, s).define();
        // x * a - s * s == -1, posted as two inequalities.
        m.linear(x * a - sq).le(-1).post()?;
        m.linear(x * a - sq).ge(-1).post()?;
    }

    let mut out = Out::new();
    out.put("number", x);
    Ok(out)
}
