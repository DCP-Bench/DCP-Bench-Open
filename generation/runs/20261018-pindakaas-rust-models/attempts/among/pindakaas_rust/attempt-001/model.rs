// Problem: among. An array x of n values, each in 0..=7, where exactly m entries of x take one of the values in v.

// All other values may be anything larger than or equal to 0 and less than or equal to 7.
fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("n");
    let m = inst.int("m");
    let v = inst.ints("v");

    // x is an array of n values, each in 0..=7.
    let xs: Vec<IntVar> = (0..n).map(|_| IntVar::new(0..=7)).collect();

    // Requires exactly m values in x to take one of the values in v.
    // For each entry, b is true exactly when the entry equals one of the values in v.
    let mut in_v: Vec<Lit> = Vec::with_capacity(n);
    for x in &xs {
        let b = s.new_lit();
        let mut clause: Vec<Lit> = vec![!b];
        for &k in &v {
            if (0..=7).contains(&k) {
                let e = reify_eq(s, iv(x), k)?;
                s.add_clause([!e, b])?;
                clause.push(e);
            }
        }
        s.add_clause(clause)?;
        in_v.push(b);
    }

    // Requires exactly m values in x to take one of the values in v.
    let mut count = LinExp::default();
    for b in in_v {
        count += LinExp::from(b);
    }
    post(s, count, Comparator::Equal, m)?;

    let mut out = Out::new();
    out.put("x", &xs);
    Ok(out)
}
