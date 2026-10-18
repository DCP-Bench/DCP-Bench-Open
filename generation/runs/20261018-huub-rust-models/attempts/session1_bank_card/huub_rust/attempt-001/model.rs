// Bank card PIN puzzle: a 4 digit PIN abcd, print the PIN (a, b, c, d).
// Facts used to remember it:

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // My bank card has a 4 digit pin, abcd.
    let a = m.new_int_decision(0..=9);
    let b = m.new_int_decision(0..=9);
    let c = m.new_int_decision(0..=9);
    let d = m.new_int_decision(0..=9);

    // no two digits are the same
    m.unique(vec![a, b, c, d]).post()?;

    // the 2-digit number cd is 3 times the 2-digit number ab
    // 10*c + d == 3 * (10*a + b)
    m.linear(c * 10 + d - a * 30 - b * 3).eq(0).post()?;

    // the 2-digit number da is 2 times the 2-digit number bc
    // 10*d + a == 2 * (10*b + c)
    m.linear(d * 10 + a - b * 20 - c * 2).eq(0).post()?;

    let mut out = Out::new();
    out.put("a", a).put("b", b).put("c", c).put("d", d);
    Ok(out)
}
