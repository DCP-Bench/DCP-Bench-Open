// Five Spanish brigands: Alfonso (A), Benito (B), Carlos (C), Diego (D) and Esteban (E).
// Find how many doubloons each had, given the band captured altogether exactly 200 doubloons,
// and that if Alfonso had twelve times as much, Benito three times as much, Carlos the same
// amount, Diego half as much and Esteban one-third as much, they would still have altogether
// just 200 doubloons. No brigand had less than one doubloon.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let _ = inst;

    // No brigand had less than one doubloon.
    let a = IntVar::new(1..=200);
    let b = IntVar::new(1..=200);
    let c = IntVar::new(1..=200);
    let d = IntVar::new(1..=200);
    let e = IntVar::new(1..=200);

    // They had altogether exactly 200 doubloons.
    post(s, iv(&a) + iv(&b) + iv(&c) + iv(&d) + iv(&e), Comparator::Equal, 200)?;

    // If Alfonso had twelve times as much, Benito three times as much, Carlos the same amount,
    // Diego half as much and Esteban one-third as much, they would still have altogether just
    // 200 doubloons. Multiplied by 6 so that every coefficient is an integer.
    post(
        s,
        scaled(&a, 72) + scaled(&b, 18) + scaled(&c, 6) + scaled(&d, 3) + scaled(&e, 2),
        Comparator::Equal,
        1200,
    )?;

    let mut out = Out::new();
    out.put("A", &a).put("B", &b).put("C", &c).put("D", &d).put("E", &e);
    Ok(out)
}
