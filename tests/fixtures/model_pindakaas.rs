fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.int("n");
    let x = IntVar::new(0..=n);
    let y = IntVar::new(0..=n);
    post(s, iv(&x) + iv(&y), Comparator::Equal, n)?;
    let mut out = Out::new();
    out.put("x", &x).put("y", &y);
    Ok(out)
}
