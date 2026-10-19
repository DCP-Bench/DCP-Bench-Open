// Problem: session5_hardy_1729_square.
// Find a combination of 4 different numbers between 1 and 100 such that the sum of the
// squares of the two first numbers is equal to the sum of the squares of the other two,
// a^2 + b^2 = c^2 + d^2. Print the numbers (a, b, c, d).

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // Find a combination of 4 different numbers between 1 and 100
    let a = IntVar::new(1..=100);
    let b = IntVar::new(1..=100);
    let c = IntVar::new(1..=100);
    let d = IntVar::new(1..=100);
    all_different(s, &[a.clone(), b.clone(), c.clone(), d.clone()])?;

    // the sum of the squares of the two first numbers is equal to the sum of the squares
    // of the other two numbers, a^2 + b^2 = c^2 + d^2
    let aa = IntVar::new(1..=10000);
    let bb = IntVar::new(1..=10000);
    let cc = IntVar::new(1..=10000);
    let dd = IntVar::new(1..=10000);
    times(s, &a, &a, &aa)?;
    times(s, &b, &b, &bb)?;
    times(s, &c, &c, &cc)?;
    times(s, &d, &d, &dd)?;
    post(
        s,
        iv(&aa) + iv(&bb) + scaled(&cc, -1) + scaled(&dd, -1),
        Comparator::Equal,
        0,
    )?;

    let mut out = Out::new();
    out.put("a", &a).put("b", &b).put("c", &c).put("d", &d);
    Ok(out)
}
