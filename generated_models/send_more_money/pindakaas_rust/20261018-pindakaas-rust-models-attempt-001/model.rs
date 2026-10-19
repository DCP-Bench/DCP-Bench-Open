// SEND + MORE = MONEY: assign a distinct digit 0..9 to each letter s, e, n, d, m, o, r, y,
// with the first letter of each word (s and m) not zero.

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // Each letter is a digit from 0 to 9; the leading letters s and m are from 1 to 9.
    let sv = IntVar::new(1..=9);
    let ev = IntVar::new(0..=9);
    let nv = IntVar::new(0..=9);
    let dv = IntVar::new(0..=9);
    let mv = IntVar::new(1..=9);
    let ov = IntVar::new(0..=9);
    let rv = IntVar::new(0..=9);
    let yv = IntVar::new(0..=9);

    // Each letter must be assigned a unique digit.
    all_different(s, &[sv.clone(), ev.clone(), nv.clone(), dv.clone(), mv.clone(), ov.clone(), rv.clone(), yv.clone()])?;

    // The equation SEND + MORE = MONEY, written as SEND + MORE - MONEY = 0:
    // 1000 s + 91 e - 90 n + d - 9000 m - 900 o + 10 r - y = 0.
    let expr = scaled(&sv, 1000)
        + scaled(&ev, 91)
        + scaled(&nv, -90)
        + scaled(&dv, 1)
        + scaled(&mv, -9000)
        + scaled(&ov, -900)
        + scaled(&rv, 10)
        + scaled(&yv, -1);
    post(s, expr, Comparator::Equal, 0)?;

    let mut out = Out::new();
    out.put("s", &sv)
        .put("e", &ev)
        .put("n", &nv)
        .put("d", &dv)
        .put("m", &mv)
        .put("o", &ov)
        .put("r", &rv)
        .put("y", &yv);
    Ok(out)
}
