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
    // The squares are the only values the square variables take, so their domains have holes
    // (a dense domain up to 10000 exhausts memory in the sum below).
    let squares: Vec<i64> = (0..=100).map(|k| k * k).collect();
    let square_domain = || pindakaas::RangeList::from_iter(squares.iter().map(|&k| k..=k));
    let aa = IntVar::new(square_domain());
    let bb = IntVar::new(square_domain());
    let cc = IntVar::new(square_domain());
    let dd = IntVar::new(square_domain());
    element_const(s, &a, &squares, &aa)?;
    element_const(s, &b, &squares, &bb)?;
    element_const(s, &c, &squares, &cc)?;
    element_const(s, &d, &squares, &dd)?;
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
