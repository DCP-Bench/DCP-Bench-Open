// General store: a cryptarithm. Each letter stands for a different digit, and the
// words above the horizontal line add up to ALL WOOL. The puzzle has no instance
// data, so the words are fixed by the description.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // Each different letter stands for a digit 0-9.
    let a = m.new_int_decision(0..=9);
    let b = m.new_int_decision(0..=9);
    let c = m.new_int_decision(0..=9);
    let e = m.new_int_decision(0..=9);
    let h = m.new_int_decision(0..=9);
    let l = m.new_int_decision(0..=9);
    let o = m.new_int_decision(0..=9);
    let p = m.new_int_decision(0..=9);
    let s = m.new_int_decision(0..=9);
    let w = m.new_int_decision(0..=9);

    // Each different letter stands for a different digit.
    m.unique(vec![a, b, c, e, h, l, o, p, s, w]).post()?;

    // The words above the line add up to ALL WOOL. The sixteen addends are written
    // as place values, so each letter gets one coefficient: the sum of its place
    // values over the addends, minus its place values in ALL WOOL.
    m.linear(
        c * 223000 + b * 101000 + e * 2342 + h * 25001 + o * 10610 + p * 1011032
            + s * 12049 + w * 111
            - a * 698690
            - l * 89790,
    )
    .eq(0)
    .post()?;

    let mut out = Out::new();
    out.put("A", a)
        .put("B", b)
        .put("C", c)
        .put("E", e)
        .put("H", h)
        .put("L", l)
        .put("O", o)
        .put("P", p)
        .put("S", s)
        .put("W", w);
    Ok(out)
}
