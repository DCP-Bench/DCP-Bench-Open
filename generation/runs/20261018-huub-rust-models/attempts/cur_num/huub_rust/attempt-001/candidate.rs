// Problem cur_num: find a number "peculiar" between 1 and 10000, other than 48,
// such that adding 1 to it gives a square number, and adding 1 to its half
// also gives a square number.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // The number, between 1 and 10000.
    let p = m.new_int_decision(1..=10000);

    // Print another number: the number is not 48.
    m.linear(p).ne(48).post()?;

    // The half of the number: p = 2 * h, so the half is a whole number.
    let h = m.new_int_decision(1..=5000);
    m.linear(p - h * 2).eq(0).post()?;

    // Adding 1 to the number gives a square number: p + 1 = a * a.
    let a = m.new_int_decision(0..=100);
    let sq_a = m.new_int_decision(0..=10001);
    m.mul(a, a).result(sq_a).post()?;
    m.linear(sq_a - p).eq(1).post()?;

    // Adding 1 to its half gives a square number: h + 1 = b * b.
    let b = m.new_int_decision(0..=100);
    let sq_b = m.new_int_decision(0..=5001);
    m.mul(b, b).result(sq_b).post()?;
    m.linear(sq_b - h).eq(1).post()?;

    let mut out = Out::new();
    out.put("peculiar", p);
    Ok(out)
}
