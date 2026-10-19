// Bank card PIN abcd: four digits a, b, c, d, each in 0..=9.
// Puzzle: find the PIN (a, b, c, d).

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let _ = inst;
    let a = IntVar::new(0..=9);
    let b = IntVar::new(0..=9);
    let c = IntVar::new(0..=9);
    let d = IntVar::new(0..=9);

    // no two digits are the same
    all_different(s, &vec![a.clone(), b.clone(), c.clone(), d.clone()])?;

    // the 2-digit number cd is 3 times the 2-digit number ab
    // 10c + d = 3 * (10a + b)
    post(
        s,
        scaled(&c, 10) + iv(&d) - scaled(&a, 30) - scaled(&b, 3),
        Comparator::Equal,
        0,
    )?;

    // the 2-digit number da is 2 times the 2-digit number bc
    // 10d + a = 2 * (10b + c)
    post(
        s,
        scaled(&d, 10) + iv(&a) - scaled(&b, 20) - scaled(&c, 2),
        Comparator::Equal,
        0,
    )?;

    let mut out = Out::new();
    out.put("a", &a).put("b", &b).put("c", &c).put("d", &d);
    Ok(out)
}
