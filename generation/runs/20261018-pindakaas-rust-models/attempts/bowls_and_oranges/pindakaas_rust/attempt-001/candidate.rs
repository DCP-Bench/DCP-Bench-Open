// Bowls and oranges: n bowls are placed in a line at intervals of 1 meter, numbered 1 to n.
// All m oranges go into the bowls, at most one orange per bowl, so that there are no three
// oranges A, B, C such that the distance between A and B equals the distance between B and C.
// Output x: the bowls holding an orange, in ascending order.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("n");
    let m = inst.size("m");

    // Occupancy: occ[b] is true when bowl b + 1 holds an orange.
    let occ: Vec<Lit> = (0..n).map(|_| s.new_lit()).collect();

    // Place all m oranges, at most one per bowl.
    let mut total = LinExp::default();
    for &o in &occ {
        total += LinExp::from(o);
    }
    post(s, total, Comparator::Equal, m as i64)?;

    // No three oranges in arithmetic progression: for bowls a < b < c with b - a = c - b,
    // not all three bowls hold an orange.
    for a in 0..n {
        for d in 1..n {
            if a + 2 * d >= n {
                break;
            }
            s.add_clause([!occ[a], !occ[a + d], !occ[a + 2 * d]])?;
        }
    }

    // Output x: the m occupied bowls in ascending order, as 1-based bowl numbers.
    let x: Vec<IntVar> = (0..m).map(|_| IntVar::new(1..=n as i64)).collect();
    for i in 0..m.saturating_sub(1) {
        post(s, iv(&x[i]) - iv(&x[i + 1]), Comparator::LessEq, -1)?;
    }
    // Each x[i] is an occupied bowl.
    for xi in &x {
        for b in 1..=n {
            let at = reify_eq(s, iv(xi), b as i64)?;
            s.add_clause([!at, occ[b - 1]])?;
        }
    }

    let mut out = Out::new();
    out.put("x", &x);
    Ok(out)
}
