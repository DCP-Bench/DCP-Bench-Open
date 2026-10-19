// Pythagorean triplet: natural numbers a, b, c with a^2 + b^2 = c^2 and a + b + c = 1000.
// The description states there is exactly one such triplet, which holds with a < b < c.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    let total: i64 = 1000;
    let hi = total - 2;

    let a = m.new_int_decision(1..=hi);
    let b = m.new_int_decision(1..=hi);
    let c = m.new_int_decision(1..=hi);

    // a < b < c
    m.linear(a).lt(b).post()?;
    m.linear(b).lt(c).post()?;

    // a + b + c = 1000
    m.linear(a + b + c).eq(total).post()?;

    // a^2 + b^2 = c^2
    let sq_max = hi * hi;
    let a2 = m.new_int_decision(1..=sq_max);
    let b2 = m.new_int_decision(1..=sq_max);
    let c2 = m.new_int_decision(1..=sq_max);
    m.mul(a, a).result(a2).post()?;
    m.mul(b, b).result(b2).post()?;
    m.mul(c, c).result(c2).post()?;
    m.linear(a2 + b2).eq(c2).post()?;

    let mut out = Out::new();
    out.put("a", a).put("b", b).put("c", c);
    Ok(out)
}
