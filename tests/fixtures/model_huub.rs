fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.int("n");
    let x = m.new_int_decision(0..=n);
    let y = m.new_int_decision(0..=n);
    let mut out = Out::new();
    if inst.flag("optimize") {
        m.linear(x + y).ge(n).post()?;
        let total = m.new_int_decision(0..=2 * n);
        m.linear(x + y).eq(total).post()?;
        out.put("x", x).put("y", y);
        out.minimise(total);
    } else {
        m.linear(x + y).eq(n).post()?;
        out.put("x", x).put("y", y);
    }
    Ok(out)
}
