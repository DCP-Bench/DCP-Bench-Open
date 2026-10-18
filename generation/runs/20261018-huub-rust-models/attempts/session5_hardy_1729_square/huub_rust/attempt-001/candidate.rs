// Problem: session5_hardy_1729_square. Find a combination of 4 different numbers
// between 1 and 100, such that the sum of the squares of the two first numbers is
// equal to the sum of the squares of the other two numbers, a^2 + b^2 = c^2 + d^2.
// Print the numbers (a, b, c, d).

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // Find a combination of 4 different numbers between 1 and 100,
    let a = m.new_int_decision(1..=100);
    let b = m.new_int_decision(1..=100);
    let c = m.new_int_decision(1..=100);
    let d = m.new_int_decision(1..=100);
    m.unique(vec![a, b, c, d]).post()?;

    // such that the sum of the squares of the two first numbers is equal to
    // the sum of the squares of the other two numbers, a^2 + b^2 = c^2 + d^2.
    let sa = m.new_int_decision(1..=10000);
    let sb = m.new_int_decision(1..=10000);
    let sc = m.new_int_decision(1..=10000);
    let sd = m.new_int_decision(1..=10000);
    m.mul(a, a).result(sa).post()?;
    m.mul(b, b).result(sb).post()?;
    m.mul(c, c).result(sc).post()?;
    m.mul(d, d).result(sd).post()?;
    m.linear(sa + sb - sc - sd).eq(0).post()?;

    let mut out = Out::new();
    out.put("a", a).put("b", b).put("c", c).put("d", d);
    Ok(out)
}
