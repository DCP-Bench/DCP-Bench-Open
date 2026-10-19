// Send More Money: assign each letter s, e, n, d, m, o, r, y a distinct digit from 0 to 9
// so that SEND + MORE = MONEY holds, with the first letters of each word not zero.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // Each letter stands for a digit from 0 to 9.
    let s = m.new_int_decision(0..=9);
    let e = m.new_int_decision(0..=9);
    let n = m.new_int_decision(0..=9);
    let d = m.new_int_decision(0..=9);
    let mm = m.new_int_decision(0..=9);
    let o = m.new_int_decision(0..=9);
    let r = m.new_int_decision(0..=9);
    let y = m.new_int_decision(0..=9);

    // Each letter must be assigned a unique digit.
    let letters = vec![s, e, n, d, mm, o, r, y];
    m.unique(letters.clone()).post()?;

    // The first letter of each word cannot be zero.
    m.linear(s).ge(1).post()?;
    m.linear(mm).ge(1).post()?;

    // SEND + MORE = MONEY.
    m.linear(
        s * 1000 + e * 100 + n * 10 + d + mm * 1000 + o * 100 + r * 10 + e,
    )
    .eq(mm * 10000 + o * 1000 + n * 100 + e * 10 + y)
    .post()?;

    let mut out = Out::new();
    out.put("d", d)
        .put("e", e)
        .put("m", mm)
        .put("n", n)
        .put("o", o)
        .put("r", r)
        .put("s", s)
        .put("y", y);
    Ok(out)
}
