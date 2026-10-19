// Five Spanish brigands (Alfonso A, Benito B, Carlos C, Diego D, Esteban E) count
// their doubloons: together they hold exactly 200, and each holds at least 1.
// Second scenario: 12*A + 3*B + C + D/2 + E/3 is still exactly 200.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    // The instance carries no data fields; the total and the multipliers are the
    // problem's own numbers from the description.
    let _ = inst;

    // each brigand has at least one doubloon (no upper bound is stated; the total bounds it)
    let a = m.new_int_decision(1..=200);
    let b = m.new_int_decision(1..=200);
    let c = m.new_int_decision(1..=200);
    let d = m.new_int_decision(1..=200);
    let e = m.new_int_decision(1..=200);

    // the brigands had altogether exactly 200 doubloons
    m.linear(a + b + c + d + e).eq(200).post()?;

    // if Alfonso had twelve times as much, Benito three times, Carlos the same,
    // Diego half and Esteban one-third, the total would still be 200.
    // Multiplied by 6 to keep integer coefficients:
    // 72*A + 18*B + 6*C + 3*D + 2*E = 1200
    m.linear(a * 72 + b * 18 + c * 6 + d * 3 + e * 2).eq(1200).post()?;

    let mut out = Out::new();
    out.put("A", a).put("B", b).put("C", c).put("D", d).put("E", e);
    Ok(out)
}
